**README** File for Lab 4 programs in Python.

It was written by *Angnuo Li* on Nov 16, 2017.

## DESCRIPTION

The default client port number is 4023.

The Lab 4 contains two program files: ftpc.py, ftps.py.
    
1. ftpc.py is to send all bytes of a local file to a troll process and the troll process will send the data to a remote server using Alternating Bit Protocol over UDP with an artificial packet loss rate.

    The default client port number is 4023.
    Sleep time between two data segments is 0.015 s.

    Firstly, the client will send the first segment: 4 bytes of filesize. The header is 8 bytes contains 4 bytes of server IP address, 2 bytes of server port number, 1 bytes of flag (flag is 1) and 1 bytes of sequence number {0,1}. The program generates sequence number periodically. After sending a packet, it waits for an ACK.
    1. If the client receives an ACK, it will check if the received ACK equals to next sequence number. If so, the transmission is successful and it will send next packet. If not, it will resend this segment immediately.
    2. If there is no response, it will resend the segment after timeout (50 ms).

    Secondly, the client will send the second segment: 20 bytes of filename. The header structure is same and the flag is 2. It will also wait for an ACK from the server and check if the transmission is successful in the same way. 

    After sending the filesize and filename successfully, the client will send a series of "chunk" data segments. Each one contains 900 bytes of data. The header structure is same and the flag is 3. If it receives a wrong ACK or timeout happens, it will resend the segment; else it will send next chunk data. 

    Finally, after all data has been transmitted, the client will send a FIN message in which the flag is 4 and break the loop without waiting for an ACK.

2. ftps.py is to received all bytes from the client using Alternating Bit Protocol over UDP and send an ACK back through a troll process with an artificial packet loss rate.

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

    After breaking the loop, the server program ftps.py checks if two files are bitwise identical. 

troll is a process to receive packets in the same host and send packets to another host. troll process can change the delay and packet drop rate. troll program is attached.

# TESTING
1. ftps.py:

    Write "python3 ftps.py <local-port-on-gamma> <troll-port-on-gamma>" to run ftps.py.
    It will print the status of every segments. The example is :
    The size of the file to be received is: 10178 bytes.
    The name of the file to be received is: image4.jpg.
    1th data segment transmission is successful. Already received filesize is 900 bytes.
    2th data segment transmission is successful. Already received filesize is 1800 bytes.
    3th data segment transmission is successful. Already received filesize is 2700 bytes.
    Warning! Found a duplicated 3th segment. Drop the segment.
    ...

    Termination message is :
    Server Termination Message:
    The two files are bitwise identical.
    The file transmission is completed and successful.
    Filesize received by the server: 10178 bytes.
    Filename received by the server: image4.jpg
    Process time: 8.185008525848389 s.

    If it is unsuccessful, it will print 
    The file transmission is completed but unsuccessful.

2. ftpc.py:

    Write "python3 ftpc.py <remote-IP-on-gamma> <remote-port-on-gamma> <troll-port-on-beta> <local-file-to-transfer>" to run ftpc.py
    It will print the status of every segments. The example is :
    Filesize of the file to be sent: 10178 bytes
    The client port number is 4023.
    Current sequence number is: 0, ACK from the server is: 1.
    Current sequence number is: 1, ACK from the server is: 0.
    The size of current segment sent to the server is: 900 bytes
    The size of rest data: 10178 bytes
    Current sequence number is: 0, ACK from the server is: 1.
    1th segment transmission successful!
    The size of current segment sent to the server is: 900 bytes
    The size of rest data: 9278 bytes
    Current sequence number is: 1, ACK from the server is: 0.
    2th segment transmission successful!
    The size of current segment sent to the server is: 900 bytes
    The size of rest data: 8378 bytes
    Current sequence number is: 0, ACK from the server is: 1.
    3th segment transmission successful!
    The size of current segment sent to the server is: 900 bytes
    The size of rest data: 7478 bytes
    Warning! 4th segment lost. Resend 4th data segment.
    ...

    Termination message is :
    Client Termination Message:
    The file transmission is completed.
    Filesize sent to the server: 10178 bytes.
    Filename received by the server: image4.jpg
    Process time: 1.7986280918121338 s.

3. troll:

    On gamma server, write "troll -C <IP-address-of-gamma> -S <IP-address-of-beta> -a <server-port-on-gamma> -b <client-port-on-beta> <troll-port-on-gamma> -r -s 1 -t -x <packet-drop-%>" to run troll process.
    On beta client, write "troll -C <IP-address-of-beta> -S <IP-address-of-gamma> -a <server-port-on-beta> -b <client-port-on-gamma> <troll-port-on-beta> -r -s 1 -t -x <packet-drop-%>" to run troll process.