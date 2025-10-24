import socket
import os
import time

serverIP = "169.226.237.49"
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
                            #print(f"Sent chunk of {len(chunk)} bytes.")
                            break
                    except socket.timeout:
                        print("Timeout, resending chunk...")
        
        # after file is sent, send FIN        
        fin, addr = clientSocket.recvfrom(1024)
        if fin == b"FIN":
            print(f"File {fileName} sent successfully.")
    
    elif message[0:4] == "GET ":
        clientSocket.sendto(message.encode('utf-8') + b'\n', (serverIP, serverPort))

        msg, addr = clientSocket.recvfrom(1024) # Receive file size
        if msg.startswith(b"LEN:"):
            total_bytes = int(msg[4:].decode())
            # send ack for length
            clientSocket.sendto(b"ACK_LEN", (serverIP, serverPort))
            print(f"Receiving file of size {total_bytes} bytes from server...")

            # step 2: receive the file in chunks
            received  = 0
            file_to_get = message[4:].strip()
            local_name = "UDP_" + os.path.basename(file_to_get)
            local_download_path = "UDP_downloads"+ "/" + local_name
            os.makedirs(os.path.dirname(local_download_path), exist_ok=True)

            with open(local_download_path, 'wb') as f:
                while received < total_bytes:
                    data, addr = clientSocket.recvfrom(1024) # buffer size is 1024 bytes
                    f.write(data)
                    received += len(data)
                    clientSocket.sendto(b"ACK", (serverIP, serverPort)) # send ack for each chunk

            # after file is received, send FIN
            print("File received completely.")
            clientSocket.sendto(b"FIN", (serverIP, serverPort))
            print(f"File {local_name} received from server.")
    message = input()
    

clientSocket.close()
