import socket
import threading
import logging


#TODO: Implement P2PTracker

connectedClients = []
check_list = [] # contains all info obtained from LOCAL_CHUNKS commands
chunk_list = [] # contains entries of file chunks whose hash has been verified by 2+ P2PClients (has entries for each of those P2PClients)

trackerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
trackerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
trackerSocket.bind(("localhost", 5100))
trackerSocket.listen(1)

logging.basicConfig(filename = "logs.log", format = "%(message)s", filemode = "a")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

while True:
    connectionSocket, addr = trackerSocket.accept()
    connectedClients.append(connectionSocket)

    def multi_threading_clients(connectionSocket):
        while True:
            message = connectionSocket.recv(1024).decode()
            if (message == ""):
                break
            message_info = message.split(',', 1)
            nocommand_msg = message_info[1]
            command = message_info[0]
            curr_index = nocommand_msg.split(',', 1)[0]
            if (command == "LOCAL_CHUNKS"):
                curr_hash = nocommand_msg.split(',', 2)[1]

                # need to verify if it has same chunks as those in check_list and if has matching hashes for those chunks (to be put in chunk_list)
                if (len(check_list) > 0):
                    for chunk in check_list:
                        chunk_info = chunk.split(',')
                        chunk_index = chunk_info[0]
                        chunk_hash = chunk_info[1]

                        # if file hashes match for the same chunk, add to chunk list because verified by at least 2 P2PClients
                        if (chunk_index == curr_index and chunk_hash == curr_hash):
                                chunk_list.append(nocommand_msg)
                                chunk_list.append(chunk)
                                print(chunk_list)
                # add info to check_list but without command
                check_list.append(nocommand_msg)
            if (command == "WHERE_CHUNK"):
                found_chunk = "no"
                for chunk in chunk_list:
                    chunk_info = chunk.split(',')
                    chunk_index = chunk_info[0]
                    chunk_hash = chunk_info[1]
                    if (curr_index == chunk_index):
                        chunk_ip = chunk_info[2]
                        chunk_port = chunk_info[3]
                        # checks to see if other P2PClient info already given
                        if (found_chunk != "no"):
                            found_chunk += ',' + chunk_ip + ',' + chunk_port
                        else:
                            # first client to have chunk -- append the entire chunk info
                            found_chunk = f"P2PTracker,GET_CHUNK_FROM,{chunk}"
                            logger.info(found_chunk)
                
                if (found_chunk == "no"):
                    # chunk location unknown for specified index
                    unknown_message = f"P2PTracker,CHUNK_LOCATION_UNKNOWN,{curr_index}"
                    connectionSocket.sendall(unknown_message.encode())
                    logger.info(unknown_message)
                else:
                    # found_chunk was filled with info about where to find chunk
                    connectionSocket.sendall(found_chunk.encode())
    thread = threading.Thread(target = multi_threading_clients, args = (connectionSocket, ))
    thread.start()
trackerSocket.close()

if __name__ == "__main__":
    pass