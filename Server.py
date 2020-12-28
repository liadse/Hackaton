
from socket import *

serverPort = 12000 #check what the ports

#create UDP socket
serverSocket = socket(AF_INET,SOCK_DGRAM)
# bind socket to local port number 12000
serverSocket.bind(('', serverPort))
print("Server Started, listening on IP address 172.1.0.44")

while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        modifiedMessage = message.upper()
        serverSocket.sendto(modifiedMessage , clientAddress)






# def handle_client(client_socket):