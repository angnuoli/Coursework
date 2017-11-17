#!/usr/bin/env python

"""
Program file: ftps.py
Nov 14, 2017

The server program is to receive all bytes from the client using Alternating Bit Protocol over UDP and send an ACK back through a troll process with an artificial packet loss rate.

The received file is stored in the "recv" sub-folder with the same filename received from the client machine.

Firstly, the server receives the first segment: 4 bytes of filesize. The header is 7 bytes contains 4 bytes of server IP address, 2 bytes of server port number, 1 bytes of flag and 1 bytes of sequence number. 
    1. If the flag is not 1 or sequence number does not match the expected value, the program will drop the packet and send expected sequence number to client. 
    2. If the packet is correct, update expected sequence number and send it as an ACK.

Secondly, the server receives the second segment: 20 bytes of filename. The header component is same. The flag should be 2 and process it in the same way.

After receiving the filesize and filename, the program creates a new file with the filename in "recv" sub-folder and it is ready to receive a series of "chunk" data segments. Each segment contains 900 bytes of data. The header is 7 bytes contains 4 bytes of server IP address, 2 bytes of server port number, 1 bytes of flag and 1 bytes of sequence number {0,1}. 
    1. If the flag is not 3 or sequence number does not match the expected value, the program will drop the packet and send expected sequence number to client. 
    2. If the packet is correct, update expected sequence number and send it as ACK. Write the data to the new file.

Finally, there are two ways to stop the program.
    1. If it receive a FIN message in which flag is 4, the program will break the loop of receiving data.
    2. If the size of received file matches the received filesize parameter and the program does not receive any packet for a while (timeout = 5s, because timeout of client is 50 ms), the program will break the loop of receiving data.

This is a stop-and-wait program. 

After breaking the loop, the program checks if two files are bitwise identical. 

The program will give a termination message.

Testing program to write "python3 ftps.py <local-port-on-gamma> <troll-port-on-gamma>" in command line. (Assume gamma is the host of server).
"""

# import os, socket, sys and hashlib module
import os
import sys
import socket
import hashlib
import time
import select

class Server:
    # identify the size of a block of bytes to be read, assume it is 900 bytes
    chunkBytesSize = 900

    # IP and port number
    HOST = ''
    PORT = 0
    socket = None
    flagExpect = 0
    troll = ()

    # ACK
    sequenceNumExpect = 0

    """docstring for Server"""
    def __init__(self):
        pass
    
    # initialize the UDP socket, bind with port number
    def initSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST, self.PORT))

    # receive the packet and check if it is the correct packet
    def isCorrectPacket(self, message):
        # the header
        clientIP = message[0:4]
        clientPort = message[4:6]
        flag = message[6] 
        sequenceNumRecv = message[7]
        if sequenceNumRecv == self.sequenceNumExpect and flag == self.flagExpect:
            # send ACK and break 
            self.sequenceNumExpect = (self.sequenceNumExpect + 1) % 2
            self.socket.sendto(self.sequenceNumExpect.to_bytes(1, byteorder='big'), self.troll)
            return True
        else :
            # send the expected sequence number
            self.socket.sendto(self.sequenceNumExpect.to_bytes(1, byteorder='big'), self.troll)
            return False

    # MD5 checksum, check if two files are bitwise identical
    def Md5(self, fileX, fileY) :
        rfile = hashlib.md5()
        sfile = hashlib.md5()

        while True:
            sdata = fileX.read(server.chunkBytesSize)
            rdata = fileY.read(server.chunkBytesSize)

            if rdata and sdata:
                rfile.update(rdata)
                sfile.update(sdata)
            else:
                break

        if rfile.hexdigest() == sfile.hexdigest():
            return True
        else :
            return False


#=================
#  Main Program
#=================

A1 = time.time()
# avoid lacking of command
if (len(sys.argv) < 3):
    print('Wrong command!')
    sys.exit(0)

# check whether the subdirectory exists or not if not create a subdirectory
subdirectory = "recv"
if not os.path.exists(subdirectory):
    os.makedirs(subdirectory)

# new class
server = Server()

# get the troll port number 
trollPort = int(sys.argv[2])
hostIP = socket.gethostbyname(socket.gethostname())
server.troll = (hostIP, trollPort)

# get the local port on the machine, initialize the socket
server.HOST = ''
server.PORT = int(sys.argv[1])
server.initSocket()

# Firstly, receive the first segment: 4 bytes of filesize
filesize = 0
server.sequenceNumExpect = 0
server.flagExpect = 1
while True:
    message, clientAddress = server.socket.recvfrom(server.PORT)
    if server.isCorrectPacket(message):
        # 4 bytes filesize data
        filesize = int.from_bytes(message[8:12], byteorder='big')
        print("The size of the file to be received is: {} bytes." .format(filesize))
        break

# Secondly, receive the second segment: 20 bytes of filename
server.flagExpect = 2
while True:
    message, clientAddress = server.socket.recvfrom(server.PORT)
    # the header
    if server.isCorrectPacket(message):
        # filename data
        received_filename = message[8:28].decode().strip()
        print("The name of the file to be received is: {}." .format(received_filename))
        break

# open the file in which we will write data
duplicated_file = open("recv/" + received_filename, 'wb')

# counter
counterSize = 0
counter = 0

# Thirdly, the program receives chunk data
guard = 0
server.flagExpect = 3
while True:
    # last wait time is 5 s
    rlist, wlist, xlist = select.select([server.socket], [], [], 5)
    if len(rlist) <= 0:
        guard += 1
        if counterSize < filesize and guard < 10: 
            continue
        else:
            break
    else:
        message, clientAddress = rlist[0].recvfrom(server.PORT)
        # the header
        flag = message[6]
        if server.isCorrectPacket(message):
            # file data 
            data = message[8:]
            duplicated_file.write(data)
            counterSize += len(data)
            counter += 1
            print("{}th data segment transmission is successful. Already received filesize is {} bytes.".format(counter, counterSize))
        elif flag != 4:
            print("Warning! Found a duplicated {}th segment. Drop the segment.".format(counter - 1))

        # if receive FIN message, break
        if flag == 4 and counterSize >= filesize:
            break

# close the file
duplicated_file.close()

# response to the clinet
received_filesize = os.path.getsize(received_filename)
print("\nThe transmission is completed\nThe size of received file: {} bytes.".format(received_filesize))

# MD5 checksum
received_file = open("recv/"+received_filename, "rb")
sended_file = open(received_filename, "rb")

# termination message
print("\nServer Termination Message:")

# MD5 checksum, check if two files are bitwise identical
if server.Md5(sended_file, received_file):
    print("The two files are bitwise identical.")
    print("The file transmission is completed and successful.")
else:
    print("The two files are not bitwise identical.")
    print("The file transmission is completed but unsuccessful.")

print("Filesize received by the server: {} bytes.\nFilename received by the server: {}" .format(received_filesize, received_filename))

# close the file and the socket
received_file.close()
sended_file.close()
server.socket.close()
print("Process time: {} s.".format(time.time() - A1))
