import socket
import argparse
import threading
import sys 
from datetime import datetime, timedelta


#TODO: Implement a client that connects to your server to chat with other clients here
parse = argparse.ArgumentParser(description = 'Client: Connection Establishment and Password Checking')
parse.add_argument('-join', action = 'store_true', required = True)
parse.add_argument('-host', type = str, required = True)
parse.add_argument('-port', type = int, required = True)
parse.add_argument('-username', type = str, required = True)
parse.add_argument('-passcode', type = str, required = True)
args = parse.parse_args()

username = args.username
clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientSocket.connect((args.host, args.port))

#TODO: Implement a client that connects to your server to chat with other clients her
#nickname = input("Choose a nickname: ")
#password = input("Enter password for client: ") #passowrd processing is on server side

#client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client.connect(('127.0.0.1', 44444)) #triggers accept method, and client is connect to server

def recieve():
	clientSocket.send(args.passcode.encode())	
	while True:
		message = clientSocket.recv(1024).decode()
		if (message == "Correct Passcode"):
			clientSocket.send(username.encode())
			print(f"Connected to {args.host} on port {args.port}")
			sys.stdout.flush()
		else:
			print(message) #if we recieve stuff that isnt a keyword we define we print so we dont do anything
			sys.stdout.flush()
			if (message == "Incorrect Passcode" or message == ":Exit"):
				break
	clientSocket.close()

def write():
	while True:
		user_input = input()
		if (user_input == ":Exit"):
			clientSocket.send(user_input.encode())
			break
		elif (user_input == ":)"):
			user_input = "[feeling happy]"
		elif (user_input == ":("):
			user_input = "[feeling sad]"
		elif (user_input == ":mytime"):
			time = datetime.now()
			user_input = time.strftime("%a %b %d %H:%M:%S %Y")
		elif (user_input == ":+1hr"):
			time = datetime.now() + timedelta(hours=1)
			user_input = time.strftime("%a %b %d %H:%M:%S %Y")
		message = f"{username}: {user_input}"
		clientSocket.send(message.encode())
	clientSocket.close()

recieve_thread = threading.Thread(target = recieve)
recieve_thread.start()
write_thread = threading.Thread(target = write)
write_thread.start() 

if __name__ == "__main__":
	pass















