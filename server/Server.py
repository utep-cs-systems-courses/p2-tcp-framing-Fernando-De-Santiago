#! /usr/bin/env python3
import socket, sys, re, os
sys.path.append("../lib")
import params
from threading import Thread,Lock

buffer1=b""
lock=Lock()

def Framedreceive(sock):
    action="get length"
    msglength=0
    global buffer1
    message=""
    while 1:
        r=sock.recv(1000)
        buffer1+=r
        if len(r)==0:
            if len(buffer1)!=0:
                os.write(1,"msg incorrect")
            return None
        if action=="get length":
            matching=re.match(b'([^:]+):(.*)',buffer1,re.DOTALL | re.MULTILINE)
            if matching:
                lengthStr,buffer1=matching.groups()
                try:
                    msglength=int(lengthStr)
                except:
                    os.write(2,("message length is invalid").encode())
                    return None
                action="get data"
            if action=="get data":
                if len(buffer1)>=msglength:
                    message=buffer1[0:msglength]
                    buffer1=buffer1[msglength:]
                return message

def run(sock):
    os.write(1,(b"Starting thread\n"))
    while 1:
        lock.acquire()
        filename=Framedreceive(sock).decode()
        print(filename)
        os.write(1,('filename is %s\n'%filename).encode())
        conf = "file name received checking if in server\n"
        os.write(1,conf.encode())
        path=os.getcwd()
        filepath=path+'/'+filename
        if os.path.isfile(filepath):
            os.write(1,('file exists now exiting\n').encode())
            sock.send(("file exists").encode())
            sys.exit(0)
        else:
            lock.release()
            sock.send(("file doesn't exist\n").encode())
            f=open(filename,"wb")
            os.write(1,b"writing file contents\n")
            message=Framedreceive(sock)
            f.write(message)
            f.close()
        sock.close()
        break

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
s.listen(2)

createfile=False
completepath=''
while True:
    conn,addr=s.accept()
    print("Connected to ",addr)
    server=Thread(target=run,args=(conn, ))
    server.start()
