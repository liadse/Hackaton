import os
import time
import sys
import tty
from socket import *
import threading
import struct
import keyboard as keyboard
from threading import *
import sys, tty, termios
from getch import getch
from select import select
from scapy.arch import get_if_addr


class color:
    # lightblue color we print with
    OKCYAN = '\033[96m'


Port = 2044
PortUDP = 13117
Buffer2048 = 2048
Buffer1024 = 1024
NumberOfListen = 20

class Client():
    """
    This class is our client class, it includes udp and tcp connection
    """

    # initialize parameters
    def __init__(self):
        self.teamName = "Cyber-Funday"
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.TimeToPlaybool = True
        self.locker = threading.Lock()
        self.connection_establish()

    # this function opens a tread in order to catch a broadcast messege and respones it
    def connection_establish(self):
        clientAnswerBroadcastT = threading.Thread(target=self.clientAnswerBroadcast)
        clientAnswerBroadcastT.start()
        clientAnswerBroadcastT.join()

    # this function creates a tcp connection and makes game preprarations
    def clientAnswerBroadcast(self):
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
        self.udpClientSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        print("Client started, listening for offer requests...")
        self.udpClientSocket.bind(('', PortUDP))
        while True:
            modifiedMessage, serverAddress = self.udpClientSocket.recvfrom(Buffer2048)
            print('Received offer from %s, attempting to connect...' % str(serverAddress))
            try:
                # devide the broadcast messege into 3 vars
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
                print(f"{color.OKCYAN}TCP connect client to " + str(serverAddress[0]) + "  " + str(portTcp))

                self.tcpClientSocket.send(b"Cyber-Funday\n")
                break
            except:
                continue
        self.udpClientSocket.close()
        self.play_the_game()

    # this function plays the keyboard game for the client
    def play_the_game(self):
        try:
            catchCharsTread = Thread(target=self.recordChars)
            # welcome meesage

            print(self.tcpClientSocket.recv(Buffer2048).decode())
            self.TimeToPlaybool = True
            catchCharsTread.start()

            self.TimeToPlaybool = False
            catchCharsTread.join()
            # bye messege
            print(self.tcpClientSocket.recv(Buffer2048).decode())
            print("Server disconnected, listening for offer requests...")
            self.tcpClientSocket.close()
            return
        except:
            self.tcpClientSocket.close()
            return

    # pycharm windows version catch keyboard
    def sendCharsToServer(self, handle):
        try:
            self.tcpClientSocket.send(handle.name.encode())
        except:
            return

    # this function records the chars and send them to the server
    def recordChars(self):
        numofchars = 0
        # the windows version
        # keyboard.on_press(self.sendCharsToServer)
        while not self.TimeToPlaybool:
            continue
        self.sendCharsToServer2(self.tcpClientSocket)

    # linux version catch keyboard
    def sendCharsToServer2(self, client_socket):
        os.system("stty raw -echo")
        previousSet = termios.tcgetattr(sys.stdin)
        try:
            tty.setcbreak(sys.stdin.fileno())

            startTime = time.time()
            while True:
                input1 = sys.stdin.read(1)
                sys.stdout.write(input1)
                client_socket.send(str.encode(input1))
                if 10 < time.time() - startTime:
                    break
            os.system("stty -raw echo")

        except:
            print("server stop")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, previousSet)
            print("Waiting")


# Start the client
client = Client()

