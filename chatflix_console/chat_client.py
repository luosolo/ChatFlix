import socket
from threading import Thread
import json
import sys
import time
from colorama import init
init(autoreset=True)



class SocketListen(Thread):
	
	def __init__(self, sock ):
		Thread.__init__(self)		
		self.running =False
		self.sock = sock
 
	def run(self):
		self.running = True		
		while self.running:
			try:			
				message = self.sock.recv(1024).decode()
				if len(message):
					print(message)
				else:
					self.running = False
			except:
				self.running= False		


if __name__ == "__main__":

	if len(sys.argv) != 4:
		print(f"Error name missing correct usage: python chat_client.py name host port")
		sys.exit()

	name = sys.argv[1]	


	SERVER_HOST = sys.argv[2]
	SERVER_PORT = int(sys.argv[3]) # server's port

	# initialize TCP socket
	s = socket.socket()
	print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
	# connect to the server
	s.connect((SERVER_HOST, SERVER_PORT))
	print("[+] Connected.")
	t = SocketListen(s)
	t.start()
	conf = "\CONFIG{}".format(json.dumps(dict(name=name)))
	s.send(conf.encode())

	if __name__ == "__main__":
		running = True
		while running:
			to_send = input()
			if to_send.lower() == 'q':
				running = False			
				t.running = False
			else:				
				s.send(to_send.encode())
		
		print("Closing connection")
		time.sleep(1)
		s.close()


