import socket
import os


serverPort = 12000
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sockname = serverSocket.getsockname()
# print(sockname)
serverSocket.bind(('',serverPort))

print("UDP Server ready...")

while True:
    
    filename_path, clientAddr = serverSocket.recvfrom(1024)
    filename = filename_path.decode('utf-8').strip()
    
    print(f"Connection from {clientAddr[0]} : {clientAddr[1]} established.")

    filename = filename_path.decode().strip() # e.g., "PUT filename.txt" or "GET filename.txt"
    

    if filename[0:4] == "PUT ":

        #step 1: receive file size, LEN:<filesize>
        msg, clientAddr = serverSocket.recvfrom(1024)
        
        if msg.startswith(b"LEN:"):
            total_bytes = int(msg[4:].decode())

            # send ack for length
            serverSocket.sendto(b"ACK_LEN", clientAddr) 
            print(f"Receiving file of size {total_bytes} bytes from {clientAddr}...")

            # step 2: receive the file in chunks
            received  = 0
            local_name = "UDP_" + os.path.basename(filename[4:])
            path_local_file = clientAddr[0] + "/" + local_name
            os.makedirs(os.path.dirname(path_local_file), exist_ok=True)
            
            with open(path_local_file, 'wb') as f:
                while received < total_bytes:
                    data, clientAddr = serverSocket.recvfrom(1024 + 32) # buffer size is 1024 bytes
                    f.write(data)
                    received += len(data)
                    serverSocket.sendto(b"ACK", clientAddr) # send ack for each chunk

            # after file is received, send FIN
            print("File received completely.")
            serverSocket.sendto(b"FIN", clientAddr)
            print(f"File {local_name} received from client.")
    