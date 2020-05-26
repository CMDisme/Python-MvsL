########################################################################
#   Author: Christopher D.                                             #                                                                      #
#   Description: My goal is to recreate the New Super Mario Bros.      #
#                DS gamemode Mario vs Luigi's multiplayer feature, but #
#                online. Even if it's not perfect, it'll be a good     #
#                starting point.                                       #
########################################################################

import socket
from _thread import *
from player import player_movement
import pygame
import pickle

server = "192.168.1.189"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    str(e)

s.listen(2)
print("Waiting for a connection, Server Started")

mario = player_movement()
luigi = player_movement()
players = [mario,luigi]

def threaded_client(conn, player):
    conn.send(pickle.dumps(players[player]))
    reply = ""
    while True:
        try:
            data = pickle.loads(conn.recv(2048))
            players[player] = data

            if not data:
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = players[0],players[1],player
                else:
                    reply = players[0],players[1],player
            conn.sendall(pickle.dumps(reply))
        except:
            break

    print("Lost connection")
    conn.close()

currentPlayer = 0
while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1


