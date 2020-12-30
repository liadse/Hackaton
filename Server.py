import threading
from socket import *
from threading import *
import struct
import time
import random
from scapy.arch import get_if_addr



class Server(object):
    """
    docstring
    """

    def __init__(self):
        # udp socket
        self.udpServerSocket = socket(AF_INET, SOCK_DGRAM)
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpServerSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # dict of connections
        self.clientsInGame = {}

        # when clients are onnected and the game starts  - will change to true

        self.firstGroup = {}
        self.secondGroup = {}

        self.locker = threading.Lock()
        #  ___________________________________________

        self.scoreFirstGroup = 0
        self.scoreSecondGroup = 0
        self.locker = threading.Lock()
        self.start_Game = False
        self.gameMode = False
        self.InitGame()

    def sendBroadcast(self):
        waitingTime = time.time() + 10

        message = struct.pack('Ibh', 0xfeedbeef, 0x2, 2044)
        # 10 sec of a brodacast send
        while time.time() < waitingTime:
            #self.udpServerSocket.sendto(message, ('<broadcast>', 14254))
            self.udpServerSocket.sendto(message, (get_if_addr('eth1'), 14254))
            # server.sendto(message, ("255.255.255.255", 13117))
            time.sleep(1)

    #  ___________________________________________

    def InitGame(self):

        self.udpServerSocket.bind(('', 2044))
        self.udpServerSocket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        self.tcpServerSocket.bind(('', 2044))
        #print(f'Server started, listening on IP address {gethostbyname(gethostname())}')
        print(f'Server started, listening on IP address {get_if_addr("eth1")}')
        self.tcpServerSocket.listen(20)
        self.tcpServerSocket.settimeout(0.2)

        broadcastT = Thread(target=self.sendBroadcast)
        broadcastT.start()

        # while broadcastT.is_alive() and not self.gameMode:
        while broadcastT.is_alive():
            try:
                with self.locker:
                    #print(self.tcpServerSocket.getsockname())
                    client_socket, client_info = self.tcpServerSocket.accept()
                    print("TCP connect server")
                    print(f"Got new connection from: {client_info}")
                    groupName = client_socket.recv(1024).decode()

                    self.clientsInGame[client_socket] = [groupName, client_info, 0, 0]
                    self.gameMode = True

            except:
                continue

        #todo check if remove
        self.udpServerSocket.close()
        self.tcpServerSocket.close()

        self.gameMode = True
        self.startGame()

    def startGame(self):
        if len(self.clientsInGame) <= -1:  # TODO check how many is the lower bound to start a game.
            print("the number of clients is:" + str(self.clientsInGame))
            print("You must To have at least 2 groups to start a game")
            # self.client_sockets_close()
            return

        list_clients = list(self.clientsInGame.keys())
        random.shuffle(list_clients)
        cut = len(list_clients) // 2
        list_1 = list_clients[:cut]
        list_2 = list_clients[cut:]

        for i in list_1:
            self.clientsInGame[i][2] = 1
            self.firstGroup[i] = self.clientsInGame[i]

        for j in list_2:
            self.clientsInGame[j][2] = 2
            self.secondGroup[j] = self.clientsInGame[j]

        firstGroupM = ""
        secondGroupM = ""
        for nameGroup1 in self.firstGroup.keys():
            firstGroupM += self.firstGroup[nameGroup1][0]+"\n"

        for nameGroup2 in self.secondGroup.keys():
            secondGroupM += self.secondGroup[nameGroup2][0]+"\n"

        for client_socket_group1 in self.firstGroup.keys():
            m = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{firstGroupM}Group 2:\n==\n{secondGroupM}\nStart pressing keys on your keyboard as fast as you can!!"
            client_socket_group1.send(m.encode())
            game_thread1 = Thread(target=self.game_thread, args=(client_socket_group1,))
            self.clientsInGame[client_socket_group1][3] = game_thread1
            game_thread1.start()

        for client_socket_group2 in self.secondGroup.keys():
            m = f"Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n{firstGroupM}Group 2:\n==\n{secondGroupM}\nStart pressing keys on your keyboard as fast as you can!!"
            client_socket_group2.send(m.encode())
            game_thread2 = Thread(target=self.game_thread, args=(client_socket_group2,))
            self.clientsInGame[client_socket_group2][3] = game_thread2
            game_thread2.start()

        for t in self.clientsInGame.keys():
            self.clientsInGame[t][3].join()

        self.start_Game = False
        if self.scoreFirstGroup > self.scoreSecondGroup:
            win = "Group 1 wins!"
            group_name = firstGroupM
        elif self.scoreFirstGroup < self.scoreSecondGroup:
            win = "Group 2 wins!"
            group_name = secondGroupM
        else:
            win = "That's a draw!"
            group_name = "Everybody wins!!!"

        for client_socket_group1 in self.firstGroup.keys():
            m = f"Game over!\nGroup 1 typed in {self.scoreFirstGroup} characters. Group 2 typed in {self.scoreSecondGroup} characters. \n{win} \n\n Congratulations to the winners:\n==\n{group_name}"
            client_socket_group1.send(m.encode())
            client_socket_group1.close()

        for client_socket_group2 in self.secondGroup.keys():
            m = f"Game over!\nGroup 1 typed in {self.scoreFirstGroup} characters. Group 2 typed in {self.scoreSecondGroup} characters. \n{win} \n\n Congratulations to the winners:\n==\n{group_name}"
            client_socket_group2.send(m.encode())
            client_socket_group2.close()


        print("Game over, sending out offer requests...")

    def game_thread(self, clientSocket):
        start_game_time = time.time()
        self.start_Game = True
        countChars = 0
        while time.time() - start_game_time < 10:
            data = clientSocket.recv(2048).decode()
            countChars += 1
        if self.clientsInGame[clientSocket][2] == 1:
            self.scoreFirstGroup += countChars
        else:
            self.scoreSecondGroup += countChars


server = Server()
