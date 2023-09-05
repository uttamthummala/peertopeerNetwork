import random
from socket import *
import threading
import os
import pickle
import random
leave=0
server = ('', 12000)
dict_file = {}
dict_posn = {}
activepeer_address = []
shareable_files = []
clientSocket = socket(AF_INET, SOCK_STREAM)
nodeSocket = socket(AF_INET, SOCK_STREAM)
nodeSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
while True:
    try:
        port = input('Enter a port to bind?\n')
        nodeSocket.bind(('', int(port)))
        nodeSocket.listen(1000)
        break
    except:
        print("Port already in use")
        continue
def request_file_offset(file,length1,length2,address,posn):
     
     res=[]
     try:
          nodeSocket2 = socket(AF_INET, SOCK_STREAM)
          nodeSocket2.connect(address)
          res.append("download")
          res.append(file)
          res.append(str(length1))
          res.append(str(length2))
          #nodeSocket2.send("download".encode())
          #nodeSocket2.send(file.encode())
          #nodeSocket2.send(str(length1).encode())
          #nodeSocket2.send(str(length2).encode())
          nodeSocket2.send(pickle.dumps(res))
          message = nodeSocket2.recv(length2-length1)
          #message = message.decode()
          #print("recieved",message)
          print("recieved a fragment of file from peer ",address," at position ",length1," of size ",length2-length1," bytes ")
          dict_file[address] = message
          dict_posn[posn] = address
          nodeSocket2.close()
     except:
          dict_file[address]= ("Error "+str(address)+" "+str(length1)+" "+str(length2)+" "+posn).encode()
          print("Error in downloading file from peer ",address," at position ",length1," of size ",length2-length1," bytes ")
          dict_posn[posn] = address
      
def request_file(file):
    # print("requesting file")
    # nodeSocket1 = socket(AF_INET, SOCK_STREAM)
     available_peers = []
     dict_file.clear()
     #print(activepeer_address)
     for address in activepeer_address:
         if address==nodeSocket.getsockname():
             continue
         req=[]
         nodeSocket1 = socket(AF_INET, SOCK_STREAM)
         nodeSocket1.connect(address)
         req.append("request")
         req.append(file)
       #  print("request sent")
         nodeSocket1.send(pickle.dumps(req))
         message = nodeSocket1.recv(1024)  #file found or not
        # print("message received")
         message=pickle.loads(message)
         #message1 = nodeSocket.recv(1024) #size of file
         if(message[0]=="file found"):
             print("file found with peer ",address)
             message1= message[1]
             available_peers.append(address)
         nodeSocket1.close()
    # print(available_peers)
     if(len(available_peers)==0):
         #print("file not found")
         return 
     length=int(message1)
     size=int(length/len(available_peers))
     offset=0
     posn=0
   #  print(available_peers)
     for address in available_peers:
          if(length-offset==0):
              break
          elif(length-offset<size):
                  threading.Thread(target=request_file_offset, args=(file,offset,length,address,str(posn))).start()
                  #nodeSocket.sendto("download".encode(), address)
                  #nodeSocket.sendto(str(offset).encode(), address)
                  #nodeSocket.sendto(str(length).encode(), address)
                  #message, address = nodeSocket.recv(length-offset)
                  #file.append(message)
                  offset+=length-offset
                  posn+=1
          else:
                  threading.Thread(target=request_file_offset, args=(file,offset,offset+size,address,str(posn))).start()
                  #clientSocket.sendto("download".encode(), address)
                  #clientSocket.sendto(str(offset).encode(), address)
                  #clientSocket.sendto(str(offset+size).encode(), address)
                  #message, address = clientSocket.recv(1024)
                  #file.append(message)
                  offset+=size
                  posn+=1
     while(len(dict_file)!=len(available_peers)):
            continue
     
     for(key,value) in dict_file.items():
            if(value[0:5]==("Error").encode()):
                 a=value.decode().split(" ")
                 dict_file.pop(key)
               #  print(value)
                 while True:
                            request_file_offset(file,int(a[2]),int(a[3]),random.choice(available_peers),a[4])
                            if(dict_file[dict_posn[a[4]]][0:5]!="Error"):
                                break
                
     file1=open("./shareable/"+file,"wb")
     for i in range(len(dict_file)):
        file1.write(dict_file[dict_posn[str(i)]])
     file1.close()
     print("file downloaded ",file)
     print("it is is in shareable folder and automatically shared")
     shareable_files.append(file)
def respond():
        while True:
            if(leave==1):
                return
            
            conn, address = nodeSocket.accept()
           # print("connected to",address)
            message= conn.recv(1024)

            message=pickle.loads(message)
           # print(message)
            if(message[0]=="request"):
               # print("got a request")
                #message = conn.recv(1024)
                
                message=message[1]
               # print(message)
                res=[]
                if(message in shareable_files):
                   # print("file found")
                    res.append("file found")
                    res.append(str(os.path.getsize("./shareable/"+message)))
                    conn.send(pickle.dumps(res))
                   # print("sent size")
                else:
                    res[0]="file not found"
                    conn.send(pickle.dumps(res))
                   # print("file not found")
            elif(message[0]=="download"):
               # print("got a download request")
                message0 = message[1]
                #message=message.decode()
                message1 = message[2]
                #message1=message1.decode()
                message2 = message[3]
               # message2=message2.decode()
                f=open("./shareable/"+message0,"rb")
                f.seek(int(message1))
                data=f.read(int(message2)-int(message1))
                conn.send(data)
               # print("sent file")
                f.close()
            conn.close()
def conn_maintain_server():
   global activepeer_address
   arr=[]
   arr.append("ping")
   arr.append(nodeSocket.getsockname())
   data=pickle.dumps(arr)
   clientSocket.connect(server)
   clientSocket.send(data)

   while True:
         if(leave==1):
             return
         
         try:
                message = clientSocket.recv(1024)
                message1= pickle.loads(message)
                if(message1==[]):
                    continue
                if(message1[0]=="just a ping"):
                 # print("got a ping from server")
                    continue
                else:
                #activepeer_address.clear()
                #print(pickle.loads(message))
                    activepeer_address= pickle.loads(message)
                #print("got a list of active peers from server",activepeer_address)
         #try:
          #    message=message.decode()
             # print("got a ping from server")
         #except:
         #     print(message)
              
             # print("got a list of active peers from server",activepeer_address)
         except:
              continue
               

def main():
     while True:
            print("1. request a file")
            print("2. add a file to shareables")
            print("3. exit")
            choice=int(input("enter your choice\n"))
            #print(choice)
            if(choice==1):
                file=input("enter the file name\n")
                request_file(file)
            elif(choice==2):
                file=input("enter the file name\n")
                if(os.path.isfile("./shareable/"+file)):
                     shareable_files.append(file)
                     print("file added to shareables\n")
                else:
                     print("file not found\n")
                     print("Please make sure the file is in shareable folder\n")
                     continue    
                
            elif(choice==3):
                arr1=[]
                arr1.append("leaving")
                arr1.append(nodeSocket.getsockname())
                data=pickle.dumps(arr1)
                #print(pickle.loads(data))
               # clientSocket.connect(server)
                clientSocket.send(data)
                leave=1
                print("exiting")
                os._exit(0)
                break
            else:
                print("invalid choice")
                continue






if not os.path.exists("./shareable"):
      
    # if the demo_folder directory is not present 
    # then create it.
    os.makedirs("./shareable")

t1=threading.Thread(target=conn_maintain_server)
t2=threading.Thread(target=respond)
#t3=threading.Thread(target=main)

t1.start()
t2.start()
main()
#t3.start()
exit(0)
t1.join()
t2.join()
#t3.join()
#t2=threading.Thread(target= send_interact_nodes)



