# Send file

import argparse
import socket
from random import randbytes # is random ~= to unique?
import os

MSG_SIZE = 1000
ACK_SIZE = 3
HEADER_SIZE = 12

try:
    parser = argparse.ArgumentParser(description="An RCMP File sender")

    parser.add_argument("-i", "--ip_address", dest="ip_address", default="localhost",
                        help="receiver hostname or IP address (default: 127.0.0.1)")
    # Sender can break sending w/ default over localhost
    parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                        help="UDP port the server is listening on (default 12345)")
    parser.add_argument("-f", "--file", dest="filename", default=None,
                        help="source file name to transmit (default=None)")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="turn verbose output on")
    args = parser.parse_args()
    # Header values 
    communicationId = randbytes(4); # Hopefully four random bytes ~ unique id
    packetNum = 0;
    fileSize = 0;

    def getNetworkIp(): # is this fn necessary (in this file)?
        '''This is just a way to get the IP address of interface this program is
        communicating over.'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]

    def getByteArray(data, commId, fileBytes, packetNum): 
        ''' Way to abstract the task of creating Header + data message to send 
        over socket '''
        # I have no idea what I am doing!!!! -- need to test header size
        fileBytes_bytes = fileBytes.to_bytes(4, byteorder='big')
        packetNum_bytes = packetNum.to_bytes(4, byteorder='big')
        total_byte = commId.join([fileBytes_bytes]) # needs to be iterable
        total_byte = total_byte.join([packetNum_bytes])
        total_byte = total_byte.join([data])
        return total_byte

    try:
        print("Opening socket on port %d" % args.port)
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    except Exception as e:
        print("Error occured during connection process: %s" % e)
        exit(1)

    try:
        with open(args.filename, "rb") as f:  
            f.seek(0, os.SEEK_END)
            fileSize = f.tell() # get full size of file
            f.seek(0, 0) # reset to end
            data = f.read(MSG_SIZE) 
            while len(data)==MSG_SIZE: 
                if args.verbose:
                    print("DEBUG: Bytes read from file: %d" % len(data))
                datagram = getByteArray(data, communicationId, fileSize, packetNum)
                if args.verbose: # based on this I'm not actually convinced this did anything
                    print("DEBUG: Bytes of message sent: %d" % len(datagram))
                file_socket.sendto( datagram, (args.ip_address,args.port) )
                packetNum+=1 # increment packetNum
                msg, rcAddr = file_socket.recvfrom(ACK_SIZE)
                if msg.decode() == "ACK":
                    if args.verbose:
                        print("ACK received.")
                    data = f.read(MSG_SIZE)
            if args.verbose:
                print("DEBUG: Bytes read from file: %d" % len(data))
            datagram = getByteArray(data, communicationId, fileSize, packetNum)
            file_socket.sendto( datagram, (args.ip_address,args.port) )
        file_socket.close()
    except FileNotFoundError:
        print("Error: File does not exist.")
except KeyboardInterrupt:
    print("caught KeyboardInterrupt")
