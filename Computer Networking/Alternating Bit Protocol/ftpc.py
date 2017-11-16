#!/usr/bin/env python

"""
Program file: ftpc.py
Nov 14, 2017

This program is to send all bytes of a local file to a troll process and the troll process will send the data to a remote server using Alternating Bit Protocol over UDP.

The client port number should match the client port number assigned to troll process.

Firstly, the client will send the first segment: 4 bytes of filesize. The header is 8 bytes contains 4 bytes of server IP address, 2 bytes of server port number, 1 bytes of flag (flag is 1) and 1 bytes of sequence number {0,1}. The program generates sequence number periodically. After sending a packet, it waits for an ACK.
    1. If the client receives an ACK, it will check if the received ACK equals to next sequence number. If so, the tranmission is successful and it will send next packet. If not, it will resend this segment immediately.
    2. If there is no response, it will resend the segment after timeout (50 ms).

Secondly, the client will send the second segment: 20 bytes of filename. The header structure is same and the flag is 2. It will also wait for an ACK from the server and check if the transmission is successful in the same way. 

After sending the filesize and filename successfully, the client will send a series of "chunk" data segments. Each one contains 900 bytes of data. The header structure is same and the flag is 3. If it receives a wrong ACK or timeout happens, it will resend the segment; else it will send next chunk data. 

Finally, after all data has been transmitted, the client will send a fin packet in which the flag is 4 and breaks the loop without waiting for an ACK.

Testing program to write "python3 ftpc.py <remote-IP-on-gamma> <remote-port-on-gamma> <troll-port-on-beta> <local-file-to-transfer>" in command line. (Assume gamme is server host, beta is client host).

The file will be received by the server and stored in the "recv" folder with the same filename in the server host.

The program will give a termination message.
"""

# import os, sys and socket module
import os
import sys
import socket
import select
import time

class Client:
    # identify the size of a block of bytes to be read, assume it is 900 bytes
    chunkBytesSize = 900

    filename = ""
    filesize = null
    socket = null

    # packet components
    payloadHead = null
    flag = 0
    sequenceNum = 0

    # IP and port number, port number should be 4023
    HOST = ''
    PORT = 4023

    """docstring for Client"""
    def __init__(self):
        
    # transform remoteIP and port to payloadHead
    def initPayloadHead(self, remoteIP, remotePort):
        self.payloadHead = b''
        for byte in remoteIP:
            self.payloadHead = self.payloadHead + int(byte).to_bytes(1, byteorder = 'big')
        self.payloadHead = self.payloadHead + remotePort

    # fit the filename in 20 bytes
    def initFilename(self):
        if (len(filename) < 20) :
            print("The filename is: {}".format(filename))
            while len(filename) < 20:
                filename = filename + " "
        elif (len(filename) > 20) :
            print("Warning! The filename is more than 20 bytes.")
            sys.exit(0)

    # initialize the UDP socket, bind with port number 4023
    def initSocket(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.HOST, self.PORT))
        print("The client port number is {}.".format(self.PORT))

    # send the data to the address
    def sendto(self, data, address):
        self.socket.sendto(self.generatePacket(data), address)

    # combine header with data to generate a packet
    def generatePacket(self, data):
        return self.payloadHead + self.flag.to_bytes(1, byteorder = 'big') + self.sequenceNum.to_bytes(1, byteorder = 'big') + data

    # check if ACK matches the sequence number
    def isACK(self):
        # wait for response, set the timeout as 50ms
        rlist, wlist, xlist = select.select([clientSocket], [], [], 0.5);
        # once get a response, check the ACK
        if len(rlist) > 0:
            ACK = int.from_bytes(rlist[0].recv(1), byteorder = 'big')
            print("Current sequence number is: {}, ACK from the server is: {}." .format(self.sequenceNum, ACK))
            if ACK == ((self.sequenceNum + 1) % 2):     # ACK matches
                self.sequenceNum = (self.sequenceNum + 1) % 2     # send next packet with (squenceNum + 1) % 2
                return True

        return False



#=================
#  Main Program
#=================

A1 = time.time()

# avoid lacking of command
if (len(sys.argv) < 5):
    print('Wrong command!')
    sys.exit(0)

# get the filename and open it
filename = str(sys.argv[4])

# check whether an input file exists or not
# open the input file
try:
    file = open(filename, 'rb')
except OSError as e:
    print('Error! No file exists!')
    sys.exit(0)

# new client
Client client;

# get the filesize, the byte order is Big-Endian
client.filesize = os.path.getsize(filename).to_bytes(4, byteorder = 'big')
print("Filesize of the file to be sent: {} bytes" .format(int.from_bytes(filesize, byteorder='big')))

# process the filename
client.filename = filename
client.initFilename()

# create a socket
client.initSocket()

# get the remote IP address and port number
remoteIP = socket.gethostbyname(str(sys.argv[1])).split('.')
remotePort = int(sys.argv[2]).to_bytes(2, byteorder = 'big')
client.initPayloadHead(remoteIP, remotePort)

# set the address of troll
# get the troll port number
trollPort = int(sys.argv[3])
hostIP = socket.gethostbyname(socket.gethostname())
troll = (hostIP, trollPort)
 
# Firstly, send the first segment: 4 bytes of filesize
client.flag = 1
client.sequenceNum = 0
while True:
    # send payloadHead, flag, sequenceNum and 4 bytes of filesize to troll process
    client.sendto(client.filesize, troll)
    if client.isACK():
        break

# send the second segment (20 bytes)
client.flag = 2
while True:
    # send filename and receive the response
    client.sendto(client.filename.encode(), troll)
    if client.isACK():
        break

# sent other data segments, set the sequence number
client.flag = 3
totalFile = 0
counter = 0
while True:
    fileContent = file.read(client.chunkBytesSize)

    # if there is no data to transmit, break the loop
    if len(fileContent) <= 0:
        # send Fin
        client.flag = 4
        client.sendto(null, troll)
        print("All data has been transmitted!")
        break

    counter = counter + 1
    while True:
        # avoid overrun UDP buffer
        time.sleep(0.015)
        # send other data segmants and receive the sequence response
        client.sendto(fileContent, troll)

        print("The size of current data segment sent to the server is: {} bytes" .format(len(fileContent)))
        print("The size of rest data: {} bytes".format(int.from_bytes(filesize, byteorder='big') - totalFile))

        if client.isACK():
            print("{}th segment transmission successful!".format(counter))
            totalFile += len(fileContent)
            break
        else:
            print("Warning! {}th Packet loss happened. Resend the {}th data packet.".format(counter, counter))


# print termination message
print("\nClient temination message:")
print("The file tranmission is completed.")
print("Firesize sent to the server: {} bytes.\nFilename recevied by the server: {}" .format(int.from_bytes(filesize, byteorder='big'), filename))

print("Process time: {} s.".format(time.time() - A1))


# close the socket and the file
file.close()
client.socket.close()