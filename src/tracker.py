import socket 
import peer
import tracker
import threading
import os

class Tracker:
    def __init__(self):
        self.log = open("tracker.txt", "a")

    def TCP(self, count, peer_id):
        self.log = open("tracker.txt", "a")
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', 3456))
        server.listen(1)
        conn_socket, addr = server.accept()
        self.log.write('PEER {id}'.format(id= peer_id))
        for i in range(count):
            self.log.write('\n')
            name = conn_socket.recv(64).decode()
            self.log.write(name)
            self.log.write('\n')

        self.log.write('\n\n')
        self.log.close()    
        conn_socket.close()

        

