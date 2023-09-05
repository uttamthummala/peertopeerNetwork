
import random
from socket import *
import threading
import pickle
 
serverSocket = socket(AF_INET, SOCK_STREAM)
# Assign IP address and port number to socket 


activepeer_address = []
activepeer_conn = []
con_addr={}
def check_availability():
    abc=["just a ping"]
    data=pickle.dumps(abc)
    for con in activepeer_conn:
        try:
            con.send(data)
            print("sending a ping to ", con_addr[con])
        except:
            print("Peer not online ", con_addr[con])
            activepeer_address.remove(con_addr[con])
            activepeer_conn.remove(con)
def broadcast():
    for con in activepeer_conn:
        try:
            data=pickle.dumps(activepeer_address)
            con.send(data)
            
        except:
            print("Peer not online ", con_addr[con])
            activepeer_address.remove(con_addr[con])
            activepeer_conn.remove(con)
            broadcast()
def printit():
    check_availability()
    broadcast()
    threading.Timer(5.0, printit).start()

serverSocket.bind(('', 12000))
serverSocket.listen(1000)
        
def add_remove_peer():
            conn, address = serverSocket.accept()
            threading.Timer(0, add_remove_peer).start()
            while True:
                message=conn.recv(2048)
                try:
                    message = pickle.loads(message)
                    #print(message)

                    if (message[0] == "ping"):
                        print("Peer added", message[1])
                        activepeer_address.append(message[1])
                        activepeer_conn.append(conn)
                        con_addr[conn] = message[1]
                        broadcast()
                    elif (message[0] == "leaving"):
                       print("Peer left ", message[1])
                       activepeer_address.remove(message[1])
                       activepeer_conn.remove(conn)
                       con_addr.pop(conn)
                       broadcast()
                       break
                except:
                    continue
            

#threading.Timer(0, printit).start()
#threading.Timer(0, add_remove_peer).start()
t1 = threading.Thread(target=printit)
t2 = threading.Thread(target=add_remove_peer)
t2.start()
t1.start()
t1.join()
t2.join() 
 
 
