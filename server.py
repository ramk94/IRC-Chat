import socket
import threading
import time

PORT = 8083
HOST = socket.gethostname()
#create a socket 
class Server:
	server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	connections=[]
	users = []#[(user_id, nickname)]
	def __init__(self):
		#Binds the server to the particular port
		self.server.bind((HOST,PORT))
		self.server.listen(5)

	def connection(self,con,adr):
		while True:
			nickname = ''
			data=con.recv(1024).decode('utf-8')
			if data:
				message = data.split()
				if message[0] == '#NICK':
					nickname = message[1]
					self.users.append((adr[1], message[1]))
					print(self.users)
					data = "server : " + self.checkNick(adr[1]) + " connected"
					for connection in self.connections:
						connection.send(data.encode('utf-8'))

			#emitting the message
				else:
					data = self.checkNick(adr[1]) + ' : ' + data
					for connection in self.connections:
						connection.send(data.encode('utf-8'))

			#when user disconnects, emit the message to all the users
			#remove the user form users and connections
			elif not data:
				#print(self.checkNick(adr[1]))
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
