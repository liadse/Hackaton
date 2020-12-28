from socket import *

serverName = 'hostname'
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.connect((serverName,serverPort))

sentence = input('Input lowercase sentence')

clientSocket.send(sentence)

modifiedSentence = clientSocket.recv(1024)

print('From Server:',modifiedSentence)

clientSocket.close()

