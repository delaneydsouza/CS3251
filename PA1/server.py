import socket 
from socket import *
import argparse
import threading
import sys 


#TODO: Implement all code for your server here

# Use sys.stdout.flush() after print statemtents

# Instructions:
# server:  
	# accept connections from clients
	# get display name passcode (plaintext)
	# verify passcode is correct
	# allow clients into chatroom
# Create a chat room on single computer
# Server program will run on port passed via command line
# "<username>: message" is the proper output, dont add new spaces and lines 

parse = argparse.ArgumentParser()
parse.add_argument('-start', action = 'store_true', required = True)
parse.add_argument('-port', type = int, required = True)
parse.add_argument('-passcode', type = str, required = True)


args = parse.parse_args()

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('127.0.0.1', args.port)) # localhost?
serverSocket.listen(1)

clients = []
usernames = []

print(f'Server started on port {args.port}. Accepting connections')
sys.stdout.flush()

#broadcast message to all clients
#def broadcast(message):
#	for client in clients:
#		client.send(message)


#handle client connection, send and recieve messages
#def handle(client): #single thread
while True:
	client_handle, addr = serverSocket.accept()
	#client, address = server.accept() #running accept, we get the client and their ip address connected to server
	clientInput = client_handle.recv(1024).decode()
	if (clientInput != args.passcode or clientInput.isalnum() == False or len(clientInput) > 5): 
		client_handle.send("Incorrect passcode".encode())
		client_handle.close()

	#			client.send('INCORRECT'.encode()) #client will know connection is refused
	#			client.close()
	else:
		#client.send('PASS'.encode()) #so client knows it has to send a password
		#password = client.recv(1024).decode()  #password
		client_handle.send("Correct Passcode".encode())
		username = client_handle.recv(1024).decode()

		welcomeMessage = f"{username} joined the chatroom" #print on server that we connected to a client
		print(welcomeMessage)
		sys.stdout.flush()
		#print(f"Connected with {str(address)}  ") #print on server that we connected to a client
	 
		for client in clients:
			client.send(welcomeMessage.encode()) #every client can see this

		clients.append(client_handle)
		usernames.append(username)

		def multi_threading_clients(client_handle): 
			while True:
				message = client_handle.recv(1024).decode()
				if (message == ":Exit"):
					index = clients.index(client_handle)
					username = usernames[index]
					usernames.remove(username)
					clients.remove(client_handle)
					exit_Message = f"{username} left the chatroom"
					for client in clients:
						client.send(exit_Message.encode())
					print(exit_Message)
					sys.stdout.flush()
					client_handle.close()
					break
				if not message:
					break
				print(message)
				sys.stdout.flush()
				for client in clients:
					client.send(message.encode())
			client_handle.close()

		#we need to run one thread for each client, must be processed at the same time	
		thread = threading.Thread(target = multi_threading_clients, args = (client_handle, ))
		thread.start()
serverSocket.close()
# Use sys.stdout.flush() after print statemtents

if __name__ == "__main__":
	pass
