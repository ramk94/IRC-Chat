import socket               # Import socket module
import threading
import sys
import time

host = socket.gethostname() # Get local machine name

port = 8084                # Reserve a port for your service.
nicks= []
class Client:

	soc=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # Create a socket object


	
	def __init__(self):
		self.soc.connect((host,port))
		#continuously run on the background
		iThread=threading.Thread(target=self.sendMsg)
		iThread.daemon = True
		iThread.start()		

		while True:
			data=self.soc.recv(1024).decode('utf-8')
			if not data:
				break
			print("["+time.strftime("%H:%M:%S")+"]"," ",data)

	def sendMsg(self):
		message=input("Please enter /nick yournickname\n")
		while True:
			self.soc.send(message.encode('utf-8'))
			message=input('')


chatclient=Client()

