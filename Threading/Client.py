#! /usr/bin/env python3
import socket, sys, re, time
sys.path.append("../lib")
import params
import os

start=0
max=0
count=0
def Framedsend(socket,payload):
    msg=str(len(payload)).encode()+b':'+payload.encode()
    while len(msg):
        sent=socket.send(msg)
        msg=msg[sent:]

def readLine():
    global start
    global max
    line=""
    char=getChar()
    while(char != "EOF" and char != ''):
        line+=char
        char=getChar()
    start=0
    max=0
    return line

def getChar():
    global start
    global max
    fd=os.open(filename,os.O_RDONLY)
    if start==max:
        start=0
        max=os.read(fd,1024)
        if max==0:
            return"EOF"
    if start < len(max):
        charArray=chr(max[start])
        start+=1
        os.close(fd)
        return charArray
    else:
        os.close(fd)
        return "EOF"
    
    
switchesVarsDefaults = (
    (('-s', '--server'), 'Server', "127.0.0.1:50001"),
    (('-d','--delay'), 'delay', "0"),
    (('-?', '--usage'),"usage",False),
    )

progname = "framedClient"
paramMap = params.parseParams(switchesVarsDefaults)

server, usage = paramMap["Server"],paramMap["usage"]

if usage:
    params.usage()

try:
    ServerHost, serverPort = re.split(":",server)
    serverPort = int(serverPort)

except:
    os.write(2, "Can't parse server: port from '%s\n'" % server)
    sys.exit(1)

s=None
for res in socket.getaddrinfo(ServerHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
        os.write(1,("Creating scok : af=%d, type=%d, proto=%d\n"%(af,socktype,proto)).encode())
        s=socket.socket(af,socktype,proto)
    except socket.error as msg:
        os.write(2,("error: %s\n"%msg).encode())
        s=None
        continue
    try:
        os.write(1,("attempting to connect to %s\n" %repr(sa)).encode())
        s.connect(sa)
    except socket.error as msg:
        os.write(2,("error: %s\n" % msg).encode())
        s.close()
        s=None
        continue
    break

if s is None:
    os.write(2,('could not open socket\n').encode())
    sys.exit(1)

delay = float(paramMap['delay'])
if delay!=0:
    os.write(1,("sleeping for {delay}s\n").encode())
    time.sleep(delay)
    os.write(1,("done sleeping\n").encode())

filename=input("What is the file you wish to run ")
data=0
sentfilename=False
writecontent=False
if filename=="exit":
    Framedsend(s,filename)
    sys.exit(0)
if os.path.isfile(filename):
    print(filename)
    if sentfilename==False:
        Framedsend(s,filename)
        createfile=True
        data=s.recv(1024).decode()
        print(data)
        if data=="file exists":
            os.write(1,("file exists now exiting").encode())
            sys.exit(0)
        else:
            os.write(1,("Received '%s'\n" %data).encode())
else:
    os.write(1,("File not found exiting now").encode())
    sys.exit(0)
content=readLine()
Framedsend(s,content)
received=s.recv(1024)
os.write(1,received)

os.write(1,("End of file reached now closing\n").encode())
s.close()
    
