import socket 
from threading import Thread
from guest import Guest
import sys
import json

from colorama import Fore
import random

color_list = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.CYAN, Fore.WHITE]



CONFIG_HEADER = "\CONFIG"

def extract_config(message):
    k = message.replace(CONFIG_HEADER,"")
    try:
        data = json.loads(k)
        return data
    except:
        return None




class Listening_Thread_Server(Thread):
    """
    This class is responsible to get the message for each guest socket
    and broadcast to the other ones
    It takes as parameters a common list of guests and the current 
    one is listening to
    """
    
    def __init__(self, clients, guest:Guest) -> None:
        Thread.__init__(self)
        self.running =False
        self.clients = clients
        self.guest = guest


    def broadcast_message(self, message, guest):
        for client in self.clients:
            if client is not guest:
                client.socket.send(message.encode())

    def run(self):
        """
        This method waits new messages and send in broadcast to every one
        Cheks also if it's a config message:
            \CONFIG{"name":"A name"} in this case he changes the name of the guest
        
        """

        self.running = True
        while self.running:
            try:
                msg = self.guest.socket.recv(1024).decode()
                
                if msg is None or len(msg)== 0:
                    # This is the case when the client died or 
                    # quit so  the server continue to receive empty messages
                    # and it shoudl stop listening it
                    self.running = False                    
                    self.clients.remove(self.guest)
                    self.guest.socket.close()
                    self.broadcast_message(f"Guest '{self.guest.name}' leaves the chat", self.guest)                    
                else:                
                    if msg.startswith(CONFIG_HEADER):
                        # We find a message configuration
                        # at the moment we manage the change name
                        # when a client join to the chat the first message will to configure is name
                        configuration = extract_config(msg)                    
                        if "name" in configuration:
                            if self.guest.name is None:
                                #The case of new guest coming 
                                self.guest.name = configuration['name']                            
                                self.broadcast_message(f"A new guest with name '{self.guest.name}' has connected", self.guest)
                                
                            else:
                                # the case of changing name
                                old_name = self.guest.name
                                self.guest.name = configuration['name']
                                self.broadcast_message(f"Guest '{old_name}' change his name to '{self.guest.name}'", self.guest)
                    else:                    
                        # A normal message
                        self.broadcast_message(self.guest.say(msg), self.guest)
            except:            
                print(f"[!] Error on receiving messages from {self.guest} removing from list")
                self.broadcast_message(f"Guest {self.guest.name} leaves the chat", self.guest)
                self.clients.remove(self.guest)
                self.running = False




if __name__ == "__main__":

    if len(sys.argv) != 3:
        print ("Error on passing parameter: usage: python chat_server.py host port")
    else:

        SERVER_HOST = sys.argv[1]
        SERVER_PORT = int(sys.argv[2])

        MAX_CONNECTION = 10
        # The guest lists
        guests = set()
        #Create the socket 
        s = socket.socket()
        #Allows a socket to bind to an address and port already in use. The SO_EXCLUSIVEADDRUSE option can prevent this.
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the socket to the host and port
        s.bind((SERVER_HOST,SERVER_PORT))

        s.listen(MAX_CONNECTION)

        print(f"[*] listeing as {SERVER_HOST}:{SERVER_PORT}")

        running = True

        while running:
            # A new client is connection it remain stuck
            # to this commnad until a new one is connected
            client_socket, client_address = s.accept()
            print(f"[+] {client_address} connected") 
            
            # We add it to the list of client and create a new 
            # thread listen it
            g = Guest(None, client_address, client_socket,random.choice(color_list))
            guests.add(g)
            listen_thread = Listening_Thread_Server(guests, g)        

            listen_thread.start()

        # At the end we close every connection
        for cs in guests:
            cs.socket.close()
        s.close()