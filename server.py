import socket
import threading
import time
import sys

PORT = 8084
HOST = socket.gethostname()
#create a socket 
class Server:
	server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	#Makes the port immediately available, addresses supplied to bind() will allow reuse of the local address
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
	connections=[]
	channel_list={}
	msg=''
	msgserv=[]
	
	users = []#[(user_id, nickname)]
	def __init__(self):
		#Binds the server to the particular port
		self.server.bind((HOST,PORT))
		self.server.listen(5)
		

	#Handles all the connection requests
	def connection(self,con,adr):
		while True:
			data=con.recv(1024).decode('utf-8')
			if data:
				message = data.split()	

				#Set a nick name for the user
				if message[0] == '/nick':
					ifnick_exist=False
					for nick in self.users:
						if nick[1]==message[1]:
							ifnick_exist=True
							break
					#print(self.users)
					if ifnick_exist==False:	
						self.users.append((adr[1], message[1]))	
						self.msgserv.append((message[1],con))
						data = "server: " + self.checkNick(adr[1]) + " Welcome to IRC chat\n"
					#for connection in self.connections:

					else:
						data=message[1] + " is being used. Enter a different nickname"

					con.send(data.encode('utf-8'))
						 
				
				#Send a private message to a user
				elif message[0] =='/prvmsg':
					flag=False
					for users in self.users:
						if users[1] == message[1]:
							flag=True
							break
					
					if flag:
						self.msg=""
						for msgs in message[2:]:
							self.msg=self.msg+" "+msgs
						data=self.names(con)+' has sent you this private message:' + self.msg
						cons=self.connect(message[1])
						name=self.names(cons)
						if(name==message[1]):
							cons.send(data.encode('utf-8'))

						self.msg=""

					else:
						err="No such Nickname"
						con.send(err.encode('utf-8'))

				#Join a channel
				elif message[0]=='/join':
					
					usr=self.names(con)
					cons=self.connect(usr)
					new_user = True
					if len(message)>1:


						for possible_channel in message[1:]:

							if possible_channel[0]!="#":
								possible_channel="#"+possible_channel

						#Check if the channel already exists, if it already exits, then just add the user and his connection information
							if possible_channel in self.channel_list:
								tests=(usr,cons)
								for nick in self.channel_list[possible_channel]:
									if nick[0] == usr:
										new_user = False
								if new_user:
									self.channel_list[possible_channel].append(tests)
								else:
									chnlmsg="You have already joined "+message[1]
									cons.send(chnlmsg.encode('utf-8'))

							else:
								tests=[(usr,cons)]
								self.channel_list[possible_channel]=tests


							info=self.channel_list.get(possible_channel)

							conns=[]
							for data in info:
								conns.append(data[1])
								
							if new_user:
								data=usr+" joined "+possible_channel
								for nums in conns:
									nums.send(data.encode('utf-8'))


					else:
						err="Insuficient command"
						con.send(err.encode('utf-8'))

				#Send message to a channnel or multiple channel if you want to send same messages	
				elif message[0]=="/channel":
					if len(message)>1:
						val=1
						channel_conn = []
						for possible_channel in message[1:]:
							if possible_channel in self.channel_list:
								#check if the user us a member of the channel
								is_member = False
								for members in self.channel_list[possible_channel]:
									if self.names(con) == members[0]:
										is_member = True
								
								#add a connection to a list to emmit message at the end
								for nick in self.channel_list[possible_channel]:
									if is_member:
										channel_conn.append((possible_channel,nick[1]))
									else:
										invalid="You are not a member of "+possible_channel
										con.send(invalid.encode('utf-8'))
										break
								val += 1
							else:
								if val == 1:
									error = "Invalid Channel"
									con.send(err.encode('utf-8'))
								break
						
							#emmit the message
						#emit_message = possible_channel+" "+self.names(con)+":"
						emit_message = ""		
						for msgs in message[val:]:
							emit_message +=" "+msgs

						for channel_user in channel_conn:
							emit_user = channel_user[0] + " " +self.names(con)+":"+emit_message+"\n"
							#print(channel_user, emit_user)
				
							channel_user[1].send(emit_user.encode('utf-8'))


									
					else:
						err="Insuficient command"
						con.send(err.encode('utf-8'))

				elif message[0]=='/quit':
					self.connections.remove(con)
					data="Server: "+self.checkNick(adr[1])+" disconnected"
					print(data)
					for connection in self.connections:
						connection.send(data.encode('utf-8'))
					con.close()
					break

				#Leave the channel
				elif message[0]=='/leave':
					if len(message)>1:
						val=0
						conns=[]

						if message[1] in self.channel_list:
							chnls=self.channel_list.get(message[1])
							for k in chnls:
								if self.names(con)==k[0]:
									break
								else:
									val+=1
	
							del self.channel_list.get(message[1])[val]
							if not bool(self.channel_list.get(message[1])):
								del self.channel_list[message[1]]			
							else:
								for nick in self.channel_list[message[1]]:
									conns.append(nick[1])

								msgs=self.names(con)+" has left the "+message[1]
								for chnlmessage in conns:
									chnlmessage.send(msgs.encode('utf-8'))	
						else:
							err="No such channel"
							con.send(err.encode('utf-8'))

					else:	
						err="Insuficient command"
						con.send(err.encode('utf-8'))
						
				elif message[0]=='/list':
					available_channel=''
					member_of_channels=''
					available_users=''
					if len(message)==1:
						for keys in self.channel_list:	
							available_channel+=keys+"\n"
						available_channel="Available channels are: \n"+available_channel
						con.send(available_channel.encode('utf-8'))

					elif len(message)==2:
						available_users=''
						if message[1] in self.channel_list:
							for k in self.channel_list.get(message[1]):
								available_users+=k[0]+"\n"
							
							if self.names(con) in available_users:
								available_users="Member of the room are: \n"+available_users
								con.send(available_users.encode('utf-8'))

							else:
								err="You don't have permission to view"
								con.send(err.encode('utf-8'))

						else:
							err="NO such channel"
							con.send(err.encode('utf-8'))
							


			#emitting the message
				else:	
					data="ERROR!!!!"+data+" is an invalid command"
					con.send(data.encode('utf-8'))

			#when user disconnects, emit the message to all the users
			#remove the user form users and connections
			elif not data:	
				self.connections.remove(con)
				data = "server : "+self.checkNick(adr[1]) +" disconnected"
				print(data)
				for connection in self.connections:
					connection.send(data.encode('utf-8'))
				self.users[:] = [user for user in self.users if user[0] != adr[1]]

				con.close()
				break
				


	def checkNick(self,user_id):
		"""Returns the nickname from users array if user_id matches user"""
		for user in self.users:
			if user[0] == user_id:
				return user[1]

	#Returns the connection information
	#It will be used later to send messages
	def connect(self,name):
		for user in self.msgserv:
			if user[0]==name:
				return user[1]

	#Based on the connection information, supply the nick name
	def names(self,cons):
		#Returns the name
		for user in self.msgserv:
			if user[1]==cons:
				return user[0]

	def run(self):
		while True:
			c,a = self.server.accept()
			sThread=threading.Thread(target=self.connection,args=(c,a))
			sThread.daemon=True
			sThread.start()
			self.connections.append(c)
			print(str(a[0])+ ':' + str(a[1]),"connected")
				
chatserver=Server()
chatserver.run()
