import socket

serverName = 'hostname'
serverPort = 12000

clientSocket = socket(socket.AF_INET, socket.SOCK_DGRAM)

message = input('Input lowercase sentence:')

clientSocket.sendto(message, (serverName,serverPort))

modifiedMessage, serverAddress = clientSocket.recvfrom(1024)

print('From Server:',modifiedMessage)

clientSocket.close()

