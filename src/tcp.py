import socket 
import peer
import tracker
import threading
import os
from cryptography.fernet import Fernet
import colorama
from colorama import Fore


key = Fernet.generate_key()
f = Fernet(key)

#def search(peers, filename, index): 
#    name_to_search = filename
#    for i in range(0, len(peers)):
#        if name_to_search in peers[i].files and (i != index):
#            sender_index = i
#            break
#    else:
#        sender_index = -1
#
#    return sender_index


def search(peers, filename, index):
    threads = [threading.Thread(target= peer.UDP_listen) for peer in peers]
    for thread in threads:
        thread.start()

    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.setblocking(0)
    lst = []
    counter = 0
    for peer in peers:
        counter += 1
        clientSocket.sendto(filename.encode(), (peer.IP, peer.port))
        if counter == len(peers) + 1:
            break
        try:
            sender_index, serverAddress = clientSocket.recvfrom(8)
            num = (sender_index.decode())
            lst.append(num)
        except IOError:
            #print('io error')
            continue

        
    clientSocket.close()
    
    if (len(lst) > 0):
        for i in range(len(lst)):
            if int(lst[i]) != index:
                return int(lst[i])
    else:
        return -1


def sync_peers(recv, send, filename):
    if recv.mode == 'download':
        thread_recv = threading.Thread(target=recv.TCP_recieve, args=(send.IP,))
    if send.mode == 'send':
        thread_send = threading.Thread(target=send.TCP_send, args=(filename, recv.IP,))
    return (thread_recv, thread_send) 


def download(thread0, thread1):
    thread0.start()
    thread1.start()
    thread0.join()
    thread1.join()
    print(Fore.GREEN+'file successfully sent'+Fore.WHITE)

def update_tracker(peers, tracker_server):
    for peer in peers:
        th = threading.Thread(target=tracker_server.TCP, args=(len(peer.files), peer.id,))
        th.start()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 3456))
        for file in peer.files:
            client.send(file.encode()) 
        client.close()
        th.join() 


def run_bittorent(peers):

    print(Fore.LIGHTCYAN_EX+'availale commands:\n 1. torrent -setMode search filename \n 2. torrent -setMode send filename'+Fore.WHITE)
    recver_index = int(input('choose a peer to enter a command: '))
    print(Fore.LIGHTMAGENTA_EX+'')
    cmd = input('[{i}] >> '.format(i = recver_index)).split(' ')

    if cmd[2] == 'search':
        sender_index = search(peers, cmd[3], recver_index)


    if sender_index != -1:
        print(Fore.GREEN+'peer {i} had the file'.format(i = sender_index)+Fore.WHITE)
        cmd = input('[{i}] >> '.format(i = sender_index)).split(' ')

        filename = cmd[3]
    
        if cmd[2] == 'send':
            peers[sender_index].set_mode('send')
            peers[recver_index].set_mode('download')
            threads = sync_peers(recv=peers[recver_index], send=peers[sender_index], filename=filename)
        download(threads[0], threads[1])
        peers[sender_index].set_mode('')
        peers[recver_index].set_mode('')
        update_tracker(peers, tracker1)
    else:
        print(Fore.MAGENTA+'file is not available in the torrent'+Fore.WHITE)




if __name__ == '__main__':
    protocol = 'TCP'
    peers = [ peer.Peer(protocol), peer.Peer(protocol), peer.Peer(protocol), peer.Peer(protocol) ] 
    tracker1 = tracker.Tracker()  
    
    while True:
        run_bittorent(peers)
        
        
        

    

    
    
  
    
    
   
    