#! /usr/bin/env python3
import socket, sys, re, os
sys.path.append("../lib")
import params

buffer1=b""
    
switchesVarDefaults = (
    (('-l', '--listenPort'),'listenPort', 50001),
    (('-?', '--usage'),"usage",False),
    )

progname="echoserver"
paramMap=params.parseParams(switchesVarDefaults)

listenPort=paramMap['listenPort']
listenAddr=''

if paramMap['usage']:
    params.usage()

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((listenAddr, listenPort))
s.listen(1)

createfile=False
contentloader=False
completepath=''
while True:
    conn,addr=s.accept()
    print("Connected to ",addr)
    if os.fork()==0:
        if createfile==False:
            save_path=os.path.expanduser('~/Documents/Lab2/p2-tcp-framing-Fernando-De-Santiago')
            files=conn.recv(1024).decode()
            os.write(1,files.encode())
            print('File received ',files)
            path=(os.path.join(save_path,'Files'))
            if os.path.exists(path):
                completepath=os.path.join(path,files)
                try:
                    f=open(completepath,'x')
                    os.write(1,("File has been created").encode())
                    conn.send("ok").encode()
                    contentloader=True
                    os.wait()
                    break
                except:
                    contentloader=True
                    break
        else:
            os.write(2,"Files already exists exiting now".encode())
conn.send(b"Ok")
conn.close()
#conn.shutdown(socket.SHUT_WR)

