import socket
import os
import time

serverIP = "10.102.173.254"
serverPort = 12000

#SOCK_DGRAM is for UDP connections
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.settimeout(1.0) # Set a timeout of 1 second

message = input()

while message != "quit":
	
    if message[0:4] == "PUT ":
        clientSocket.sendto(message.encode('utf-8') + b'\n', (serverIP, serverPort))



        # home/desktop/.../client/filename
        fileName = message[4:].strip()
        local_name = os.path.basename(fileName) # Real name of the file

        fileSize = os.path.getsize(local_name) # Size of the file to be sent

        clientSocket.sendto(f"LEN:{fileSize}".encode(), (serverIP, serverPort)) # Send file size first

        msg, _ = clientSocket.recvfrom(1024) # Wait for server ack

        if msg != b"ACK_LEN":
            print("No ACK from server, aborting...")
            break
        elif msg == b"ACK_LEN":
            print("ACK_LEN received from server, sending file...")

        # now send the file
        # in chunks
        
        with open(local_name, 'rb') as f:
            while True:
                chunk = f.read(1000) # Read 1000 bytes at a time
                if not chunk:
                    break

                while True:
                    clientSocket.sendto(chunk, (serverIP, serverPort))
                    try:
                        ack, addr = clientSocket.recvfrom(1024)
                        if ack == b"ACK":
                            break
                    except socket.timeout:
                        print("Timeout, resending chunk...")
        
        # after file is sent, send FIN        
        fin, addr = clientSocket.recvfrom(1024)
        if fin == b"FIN":
            print(f"File {fileName} sent successfully.")
        
    message = input()
    

clientSocket.close()
