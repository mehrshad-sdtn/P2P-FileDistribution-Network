import socket
import threading
import os
import pickle
from cryptography.fernet import Fernet
import tcp
import colorama
from colorama import Fore

PORT = 1234
SIZE = 512
UDP_BASE = 2345


class Peer:
    peers_count = 0
    def __init__(self, protocol):
        self.id = Peer.peers_count
        self.protocol = protocol
        self.files = os.listdir('peers_media/peer_{id}'.format(id = self.id))
        self.IP = 'localhost'
        self.mode = ''
        self.port = UDP_BASE + self.id
        self.logs = open("log_files/peer_{id}.txt".format(id = self.id), "a")
        print(Fore.LIGHTBLUE_EX+str(Peer.peers_count)+Fore.WHITE)
        Peer.peers_count += 1
    

    def set_mode(self, mode):
        self.mode = mode


    def has_file(self, filename):
        return filename in self.files


    def find_file(self, filename):
        index = self.files.index(filename)
        return open('peers_media/peer_{id}/{name}'.format(id = self.id, name=self.files[index]), 'rb')


    def add_file(self, filename):
        if not (filename in self.files):
            self.files.append(filename)



    def TCP_recieve(self, sender_IP):
        #server setup
        f = tcp.f
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('', PORT))
        server.listen(1)
        conn_socket, addr = server.accept()
       
        props = pickle.loads(conn_socket.recv(1024))
        filename = props[0]
        header_size = props[1]
       
        file = open('peers_media/peer_{id}/{name}'.format(id = self.id, name = filename), 'wb')
        file_chunk = conn_socket.recv(1024)

        self.logs = open("log_files/peer_{id}.txt".format(id = self.id), "a")

        counter = 0
        while file_chunk:
            counter += 1
            dec_chunk = f.decrypt(file_chunk)
            self.logs.write(
                'packet number {num} from: {src}: \n'.format(num = counter, src= sender_IP)
                )    
            self.logs.write(
                'payload: {payload}: \n\n'.format(payload= dec_chunk)
                )     
            #file.write(file_chunk[header_size:])
            file.write(dec_chunk)
            file_chunk = conn_socket.recv(1024)
            
            
        close_resources([conn_socket, file, self.logs])
        self.add_file(filename)     
           
        
     
    def TCP_send(self, filename, recver_IP):
        f = tcp.f
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', PORT)) 
  
        raw_header = [self.IP, recver_IP]
        header = pickle.dumps(raw_header)
        header_size = len(header)

        file = self.find_file(filename)
        props = pickle.dumps([filename, header_size])
        client.send(props) 

        self.logs = open("log_files/peer_{id}.txt".format(id = self.id), "a")

        file_data = file.read(SIZE)
        counter = 0
        while file_data:
            counter += 1      
            print('')
            self.logs.write(
                'packet number {num} from: {src} to: {dest}\n\n'.format(num = counter,src = raw_header[0], dest = raw_header[1])
                )
            self.logs.write(
                'payload: {payload}: \n\n'.format(payload= file_data)
                ) 
               
            client.send(f.encrypt(file_data))
            #client.send(file_data)
            file_data = file.read(SIZE)

        close_resources([client, file, self.logs])


    def UDP_listen(self):
        serverSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
        serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        serverSocket.bind(('', self.port))
        print('peer {id} is listening ...'.format(id = self.id))
        name, clientAddress = serverSocket.recvfrom(2048)
        filename  = (name.decode())
        if self.has_file(filename):
            serverSocket.sendto(str(self.id).encode(), clientAddress)
        serverSocket.close()
        print('closed')
        return
        

def close_resources(lst):
    for resource in lst: 
        resource.close()  