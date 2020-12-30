import os
import time
import sys
import tty
from socket import *
import threading
import struct
import keyboard as keyboard
from threading import *
# import msvcrt
import sys, tty, termios
from getch import getch
from select import select
from scapy.arch import get_if_addr


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Client():

    # def __init__(self, ip, port, teamName):
    def __init__(self):
        self.teamName = "Cyber-Funday"
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.TimeToPlaybool = True
        self.locker = threading.Lock()
        self.connection_establish()

    def connection_establish(self):

        clientAnswerBroadcastT = threading.Thread(target=self.clientAnswerBroadcast)
        clientAnswerBroadcastT.start()
        clientAnswerBroadcastT.join()

    def clientAnswerBroadcast(self):
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.udpClientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        print("Client started, listening for offer requests...")
        self.udpClientSocket.bind(('', 14254))
        while True:
            modifiedMessage, serverAddress = self.udpClientSocket.recvfrom(2048)
            print('Received offer from %s, attempting to connect...' % str(serverAddress))
            try:
                magicCookie, message_type, portTcp = struct.unpack('Ibh', modifiedMessage)
            except:
                print(modifiedMessage)
                continue

            if magicCookie != 0xfeedbeef:
                continue

            break
        while True:
            try:
                self.tcpClientSocket.connect((serverAddress[0], portTcp))
                print(f"{bcolors.OKCYAN}TCP connect client to " + str(serverAddress[0]) + "  " + str(portTcp))

                self.tcpClientSocket.send(b"Cyber-Funday\n")
                break
            except:
                continue
        self.udpClientSocket.close()
        self.play_the_game()

    def play_the_game(self):
        try:
            catchCharsTread = Thread(target=self.recordChars)
            # welcome meesage

            print(self.tcpClientSocket.recv(2048).decode())
            self.TimeToPlaybool = True
            catchCharsTread.start()

            self.TimeToPlaybool = False
            catchCharsTread.join()
            # bye messege
            print(self.tcpClientSocket.recv(2048).decode())
            print("Server disconnected, listening for offer requests...")
            self.tcpClientSocket.close()
            return
        except:
            self.tcpClientSocket.close()
            return

    def sendCharsToServer(self, handle):
        try:
            self.tcpClientSocket.send(handle.name.encode())
        except:
            return

    def recordChars(self):
        numofchars = 0
        # keyboard.on_press(self.sendCharsToServer)
        while not self.TimeToPlaybool:
            continue
        self.sendCharsToServer2(self.tcpClientSocket)

    def isData(self):
        import select
        return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

    def sendCharsToServer2(self, client_socket):
        os.system("stty raw -echo")
        previousSet = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            startTime = time.time()
            while True:
                # data,a,b = select([sys.stdin],[],[],0)
                # if data:
                input1 = sys.stdin.read(1)
                # print(input1.encode('utf-8'))
                sys.stdout.write(input1)
                # client_socket.send(input1.encode('utf-8'))
                client_socket.send(str.encode(input1))
                if 10 < time.time() - startTime:
                    break
            os.system("stty -raw echo")

        except:
            print("server stop")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previousSet)
            print("Waiting")
            # client_socket.close()


client = Client()

