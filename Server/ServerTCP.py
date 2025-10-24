import socket
import os

# Getting port number from user
port = input("Enter port number to listen on: ")
serverPort = int(port)

#SOCK_STREAM is for TCP connections`
serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# Bind the socket to server address and server port
serverSocket.bind(("",serverPort))
serverSocket.listen(1)
print("The server is ready to receive")

while True:
    connectionSocket, clientAddress = serverSocket.accept()
    with connectionSocket:
        print(f"Connection from {clientAddress[0]}  :  {clientAddress[1]} established.")

        # Receiveing file name from client
        filename_bytes = b''
        # Read until newline character
        while not filename_bytes.endswith(b'\n'):
            chunk = connectionSocket.recv(1)
            if not chunk:
                break
            filename_bytes += chunk # adding received bytes

        filename = filename_bytes.decode('utf-8').strip()
        # handling PUT 
        if filename.startswith("PUT "):
            filename = filename[4:]

            client_file = os.path.basename(filename)
            print(f"Receiving file: {client_file}")
            full_path = clientAddress[0] + "/" + client_file
            # create new directory for client if does not exist already
            file_upload = os.makedirs(os.path.dirname(full_path), exist_ok=True)


            with open(full_path, 'wb') as f:
                while True:
                    data = connectionSocket.recv(4096)
                    if not data:
                        f.close()
                        break
                    f.write(data)
            
            print(f"File {client_file} received from client.")
        # handling GET
        elif filename.startswith("GET "):
            filename = filename[4:]
            print(f"Sending file: {filename}")

            with open(filename, 'rb') as f:
                while True:
                    bytesRead = f.read(4096)
                    if not bytesRead:
                        f.close()
                        break
                    connectionSocket.sendall(bytesRead)
            print(f"File {filename} sent to client.")


    connectionSocket.close()