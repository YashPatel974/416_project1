import socket
import os



# Asking the user for server IP and port number
ip = input("Enter Server IP : ")
serverIP = ip

port = input("Enter Port Number : ")
serverPort = int(port)
#SOCK_STREAM is for TCP connections
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

# Getting user input for commands
message = input()

while message != "quit":
    # handling PUT
    if message[0:4] == "PUT ":

        fileName = message
        # Send file name to server
        clientSocket.sendall(fileName.encode('utf-8') + b'\n')   
        fileName = message[4:]
        # Uploading the file to server
        with open(fileName, 'rb') as f:
            while True:
                bytesRead = f.read(4096)
                if not bytesRead:
                    f.close()
                    break
                clientSocket.sendall(bytesRead) # Send file data to server
        print(f"File {fileName} sent to server.")

    # handling GET
    elif message[0:4] == "GET ":

        fileName = message
        # Send file name to server
        clientSocket.sendall((message.strip() + "\n").encode('utf-8'))

        requested = message[4:].strip()
        #local_name = "downloaded_" + os.path.basename(requested)
        local_name = os.path.basename(requested)
        full_path = "downloads" + "/" + local_name
        # create new directory for downloads if does not exist already
        file_upload = os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Downloading the file from server, and saving it locally.
        with open(full_path, 'wb') as f:
            while True:
                data = clientSocket.recv(4096)
                if not data:
                    f.close()
                    break
                f.write(data)
        print(f"File {fileName} received from server.")

    clientSocket.close()
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientSocket.connect((serverIP, serverPort))
    message = input() # Getting user input for commands again.

print("Client exiting...")
clientSocket.close()