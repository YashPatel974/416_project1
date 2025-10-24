import socket
import os

# asking for port number to listen on from user
port = input("Enter port number to listen on: ")
serverPort = int(port)

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
                    #data, clientAddr = serverSocket.recvfrom(1024 + 32)
                    data, clientAddr = serverSocket.recvfrom(1024) # buffer size is 1024 bytes
                    f.write(data)
                    received += len(data)
                    serverSocket.sendto(b"ACK", clientAddr) # send ack for each chunk
                    print(f"ACK -> {len(data)} bytes.")

            # after file is received, send FIN
            print("File received completely.")
            serverSocket.sendto(b"FIN", clientAddr)
            print(f"File {local_name} received from client.")
    
    elif filename[0:4] == "GET ":
        file_to_send = filename[4:].strip()
        local_name = os.path.basename(file_to_send)

        file_size = os.path.getsize(local_name)
        print(f"Sending file {local_name} of size {file_size} bytes to {clientAddr}...")

        serverSocket.sendto(f"LEN:{file_size}".encode(), clientAddr) # Send file size first

        msg, clientAddr = serverSocket.recvfrom(1024) # Wait for client ack
        if msg != b"ACK_LEN":
            print("No ACK from client, aborting...")
            continue
        elif msg == b"ACK_LEN":
            print("ACK_LEN received from client, sending file...")
        
        # now send the file in chunks
        with open(local_name, 'rb') as f:
            while True:
                chunk = f.read(1000) # Read 1000 bytes at a time
                if not chunk:
                    break

                while True:
                    serverSocket.sendto(chunk, clientAddr)
                    try:
                        ack, addr = serverSocket.recvfrom(1024)
                        if ack == b"ACK":
                            print(f"rcv-> {len(chunk)} bytes.")
                            break
                    except socket.timeout:
                        print("Timeout, resending chunk...")
            
        # after file is sent, wait for FIN
        fin, addr = serverSocket.recvfrom(1024)
        if fin == b"FIN":
            print(f"File {file_to_send} sent successfully to {clientAddr}.")
        else:
            print("No FIN received, something went wrong.")