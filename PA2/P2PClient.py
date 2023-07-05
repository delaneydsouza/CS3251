from socket import *
import argparse
from threading import Thread
import sys
import hashlib
import time
import logging
import os

#TODO: Implement P2PClient that connects to P2PTracker
def hash_file(filename):
	hash_lib = hashlib.sha1()
	with open(filename, 'rb') as file:
		for chunk in iter(lambda: file.read(1024), b''):
			hash_lib.update(chunk)
	return hash_lib.hexdigest()

if __name__ == "__main__":
	def sendChunks(peerConn):
		peer_request = peerConn.recv(1024).decode()
		
		if peer_request.split(",")[0] == "REQUEST_CHUNK":
			chunk_idx = peer_request.split(",")[1]
			path = folder_path + "/chunk_" + chunk_idx
			
			with open(path, "rb") as file:
			#   for data in iter(lambda: file.read(1024), b''):
			#       peerConn.send(data)		
				data = file.read(1024)
				while data:
					peerConn.send(data)
					data = file.read(1024)
		peerConn.close()

	def receiveChunks(trackerSocket):
		while True:
			for i in range(1, last_idx + 1):
				if len(chunks) == last_idx:
					break
				if i in chunks:
					continue
				
				peer_request = "WHERE_CHUNK," + str(i)
				logger.info(f"{name},{peer_request}")
				trackerSocket.send(peer_request.encode())
				time.sleep(0.5)

				response = trackerSocket.recv(1024).decode()
				if response.startswith("CHUNK_LOCATION_UNKNOWN"):
					continue
				elif response.startswith("GET_CHUNK_FROM"):
					hash = response.split(",")[2]
					ip_addr = response.split(",")[3]
					port = response.split(",")[4]
					
					peerSocketOutgoing = socket(AF_INET, SOCK_STREAM)
					peerSocketOutgoing.connect((ip_addr, int(port)))
					logger.info(name + "," + "REQUEST_CHUNK," + str(i) + "," + ip_addr + "," + port)
					peerSocketOutgoing.send(("REQUEST_CHUNK," + str(i)).encode())
					
					time.sleep(0.5)
					file_name = "chunk_" + str(i)
					
					with open(folder_path + "/" + file_name, "wb") as file:
						while True:
							chunk = peerSocketOutgoing.recv(1024)
							if chunk == b'' or not chunk:
								break
							file.write(chunk)
					
					peerSocketOutgoing.close()
					chunks.add(i)
					chunk_str = f"LOCAL_CHUNKS,{i},{hash},localhost,{transfer_port}"
					logger.info(f"{name},{chunk_str}")
					trackerSocket.send(chunk_str.encode())
					time.sleep(0.5)
				
	parser = argparse.ArgumentParser()
	parser.add_argument("-folder", help = "folder path", type = str)
	parser.add_argument("-transfer_port", help = "port #", type = int)
	parser.add_argument("-name", help = "name", type = str)
	args = parser.parse_args()

	folder_path = args.folder
	transfer_port = args.transfer_port

	trackerSocket = socket(AF_INET, SOCK_STREAM)
	trackerSocket.connect(("127.0.0.1", 5100))
	peerSocket = socket(AF_INET, SOCK_STREAM)
	peerSocket.bind(('', transfer_port))
	peerSocket.listen(10)

	logging.basicConfig(filename ='logs.log', format = '%(message)s', filemode = 'a')
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	
	global chunks
	chunks = set()

	global name
	name = args.name

	with open(folder_path + "/local_chunks.txt", "r") as file:
		for line in file:
			chunk_idx, chunk_file = line.strip().split(",")

			if chunk_file == "LASTCHUNK":
				global last_idx
				last_idx = int(chunk_idx)
				break

			chunks.add(int(chunk_idx))

			path = folder_path + "/" + chunk_file
			hash = hash_file(path)
			msg = f"LOCAL_CHUNKS,{chunk_idx},{hash},localhost,{transfer_port}"
			logger.info(f"{name},{msg}")
			trackerSocket.send(msg.encode())
			time.sleep(0.5)
			

	receiveThread = Thread(target=receiveChunks, args=(trackerSocket,))
	receiveThread.start()

	while True:
		peerConn, addr = peerSocket.accept()
		sendThread = Thread(target=sendChunks, args=(peerConn,))
		sendThread.start()