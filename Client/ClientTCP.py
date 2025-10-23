import socket
import os

#169.226.251.1
serverIP = "169.226.251.1"
serverPort = 12000
#SOCK_STREAM is for TCP connections
clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

message = input()

while message != "quit":
    if message[0:4] == "PUT ":
        #fileName = message[4:]
        fileName = message
        
        clientSocket.sendall(fileName.encode('utf-8')) # Send file name to server
        fileName = message[4:]
        with open(fileName, 'rb') as f:
            while True:
                bytesRead = f.read(4096)
                if not bytesRead:
                    f.close()
                    break
                clientSocket.sendall(bytesRead)
        print(f"File {fileName} sent to server.")
    elif message[0:4] == "GET ":
        #fileName = message[4:]
        fileName = message
        clientSocket.sendall(fileName.encode('utf-8')) # Send file name to server
        #fileName = message[4:]
        with open("downloaded_" + fileName, 'wb') as f:
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
    message = input()

print("Client exiting...")
clientSocket.close()