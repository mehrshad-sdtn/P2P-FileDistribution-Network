import socket 
import peer
import threading
import os




if __name__ == '__main__':
    protocol = 'UDP'
    peers = [ peer.Peer(protocol), peer.Peer(protocol), peer.Peer(protocol) ] 
    
    threads = [threading.Thread(target= peer.UDP_listen) for peer in peers] 
    for thread in threads:
        thread.start()
    sender_thread = threading.Thread(target= peers[1].UDP_download, args=('cat.jpg',peers,))
    sender_thread.start()
    
    

        
        

    
