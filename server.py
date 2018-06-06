import socket
import threading
import time

PORT = 8084
HOST = socket.gethostname()
#create a socket 
class Server:
	server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	connections=[]
	channel_list={}
	default_channel='IRCDEF'
	msg=''
	ports=[]
	msgserv=[]
	default_message="Here are the list of commands\n/join channel_name----Join a channel\n/list channels----List available channels\n/list users----List users in current channel\n/kick name----Kick user from channel\n/pvmsg name----Send a private message\n/quit----Quit the chat\n"
	
	users = []#[(user_id, nickname)]
	def __init__(self):
		#Binds the server to the particular port
		self.server.bind((HOST,PORT))
		self.server.listen(5)

	def connection(self,con,adr):
		#self.ports.append(adr)
		while True:
			data=con.recv(1024).decode('utf-8')
			if data:
				message = data.split()	
				if message[0] == '#NICK':
					self.users.append((adr[1], message[1]))	
					self.msgserv.append((message[1],con))
					data = "#"+self.default_channel+" server: " + self.checkNick(adr[1]) + " Welcome to the Default Channel\n"
					for connection in self.connections:
						connection.send(data.encode('utf-8'))

				elif message[0] =='/prvmsg':

					self.msg=""
					for msgs in message[2:]:
						self.msg=self.msg+" "+msgs
					data=self.names(con)+' has sent you this private message:' + self.msg
					cons=self.connect(message[1])
					name=self.names(cons)
					if(name==message[1]):
						cons.send(data.encode('utf-8'))

					self.msg=""


				elif message[0]=='/join':
					
					usr=self.names(con)
					cons=self.connect(usr)
					new_user = True
					if len(message)>1:

						if message[1][0]!="#":
							message[1]="#"+message[1]

						#Check if the channel already exists, if it already exits, then just add the user and his connection information
						if message[1] in self.channel_list:
							tests=(usr,cons)
							for nick in self.channel_list[message[1]]:
								if nick[0] == usr:
									new_user = False
							if new_user:
								self.channel_list[message[1]].append(tests)
							else:
								chnlmsg="You have already joined "+message[1]
								cons.send(chnlmsg.encode('utf-8'))

						else:
							tests=[(usr,cons)]
							self.channel_list[message[1]]=tests


						info=self.channel_list.get(message[1])

						conns=[]
						for data in info:
							conns.append(data[1])
								
						if new_user:
							data=usr+" joined "+message[1]
							for nums in conns:
								nums.send(data.encode('utf-8'))


					else:
						err="Insuficient command"
						con.send(err.encode('utf-8'))

					
				elif message[0]=="/channel":
					if len(message)>1:
						val=1
						channel_conn = []
						for possible_channel in message[1:]:
							if possible_channel in self.channel_list:
								for nick in self.channel_list[possible_channel]:
									channel_conn.append(nick[1])
								val += 1
							else:
								if val == 1:
									error = "Invalid Channel"
									con.send(err.encode('utf-8'))
								break
						
						emit_message = self.names(con)
							
						for msgs in message[val:]:
							emit_message+=" "+msgs

						for channel_user in channel_conn:
							channel_user.send(emit_message.encode('utf-8'))

									
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

			#emitting the message
				else:	
					data="ERROR!!!!"+data+" is an invalid command"
					con.send(data.encode('utf-8'))

			#when user disconnects, emit the message to all the users
			#remove the user form users and connections
			elif not data:
				#print(self.checkNick(adr[1]))
				self.connections.remove(con)
				data = "server : "+self.checkNick(adr[1]) +" disconnected"
				print(data)

				#search in all channels 
					#if in channel remove the user and emmit the message to other members

				#emmit the message
				for connection in self.connections:
					connection.send(data.encode('utf-8'))
				#self.users[:] = [user for user in self.users if user[0] != adr[1]]

				con.close()
				break


	def checkNick(self,user_id):
		"""Returns the nickname from users array if user_id matches user"""
		for user in self.users:
			if user[0] == user_id:
				return user[1]

	def sendprvmsg(self,msg):
		self.sendprvmsg.sendto(msg,self.ports[2])


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
			self.ports.append(a)
			print(str(a[0])+ ':' + str(a[1]),"connected")
	
chatserver=Server()
chatserver.run()
