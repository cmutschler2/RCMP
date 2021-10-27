# Send file

import argparse
import socket
from random import randbytes # is random ~= to unique?
import os

MSG_SIZE = 50
ACK_SIZE = 3
HEADER_SIZE = 12

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

def getByteArray(data, commId, fileBytes, packetNum): 
    ''' Way to abstract the task of creating Header + data message to send 
    over socket '''
    empty_bytes = bytes(''.encode('utf-8')); # apparently needs an empty bytes object to concat with otherwise join does nothing
    fileBytes_bytes = fileBytes.to_bytes(4, byteorder='big')
    packetNum_bytes = packetNum.to_bytes(4, byteorder='big')
    total_byte = commId.join([empty_bytes, fileBytes_bytes]) # needs to be iterable
    total_byte = total_byte.join([empty_bytes, packetNum_bytes])
    total_byte = total_byte.join([empty_bytes, data])
    print('*'*30+"First Message" + '*'*30)
    print('empty_bytes (bytes)', end = ''); print(empty_bytes);
    print('commId    (bytes) ', end = ''); print( commId, end = ''); print('\t|\t should be 4 rand bytes')
    print('fileBytes (Int) ',end =''); print(fileBytes, end=''); print('\t|\t fileBytes (bytes) ', end=''); print(fileBytes_bytes)
    print('packetNum (Int) ',end =''); print(packetNum, end=''); print('\t|\t packetNum (bytes) ', end=''); print(packetNum_bytes)
    print('data      (bytes) ', end = ''); print(data, end=''); print('\t|\t should be 50 bytes from start of file')
    print('\t' + '*'*26+"whole Message" + '*'*30)
    print('total_bytes (bytes)', end=''); print(total_byte, end=''); print('\t|\t' + 'should be 62 bytes total, joined all of previous');
    return total_byte

print("Opening socket on port %d" % args.port)
file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
try:
    with open("testFile.txt", "rb") as f:  
        f.seek(0, os.SEEK_END)
        fileSize = f.tell() # get full size of file
        f.seek(0, 0) # reset to end
        data = f.read(MSG_SIZE) 
        print("DEBUG: Bytes read from file: %d" % len(data))
        datagram = getByteArray(data, communicationId, fileSize, packetNum)
        print("DEBUG: Bytes of message sent: %d" % len(datagram))
        file_socket.sendto( datagram, (args.ip_address,args.port) )
        packetNum+=1 # increment packetNum
        msg, rcAddr = file_socket.recvfrom(ACK_SIZE)
        if msg.decode() == "ACK":
            if args.verbose:
                print("ACK received.")
        f.close()
    file_socket.close()

except FileNotFoundError:
    print("Error: File does not exist.")
