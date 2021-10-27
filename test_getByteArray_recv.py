# Receive the file

import argparse
import socket
from pathlib import Path

MSG_SIZE = 50 
HEADER_SIZE = 12
parser = argparse.ArgumentParser(description="An RCMP File recipient")

parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                    help="UDP port the server is listening on (default 12345)")
parser.add_argument("-f", "--file", dest="filename", default="",
                    help="destination file name for incoming transmission (default='')")
parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                    help="turn verbose output on")
args = parser.parse_args()

def getNetworkIp():
    '''This is just a way to get the IP address of interface this program is
    communicating over.'''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]

file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ip_address = getNetworkIp()
print("Socket opening at %s on port" % ip_address, args.port)
addr = ( ip_address, args.port )

file_socket.bind(addr)

msg, sdAddr = file_socket.recvfrom(MSG_SIZE+HEADER_SIZE)

print('*'*30+"First Message" + '*'*30)
print('Length of Whole Msg: %d', len(msg))
print('total_bytes (bytes)', end=''); print(msg, end=''); print('\t|\t' + 'should be 62 bytes total, joined all of previous');
print('\t' + '*'*26+"Broken Message" + '*'*30)
print('commId    (bytes) ', end=''); print(msg[0:4] , end=''); print('\t|\t' + 'should be 0:3 - same every time')
print('fileBytes (bytes) ', end=''); print(msg[4:8] , end=''); print('\t|\t' + 'should be 4:7 - same every time')
print('packetNum (bytes) ', end=''); print(msg[8:12], end=''); print('\t|\t' + 'should be 8:11 - incr every time')
print('data      (bytes) ', end=''); print(msg[12:] , end=''); print('\t|\t' + 'should be 50 bytes from start of file')
 
file_socket.sendto( bytes("ACK".encode("utf-8")), sdAddr)
file_socket.close()

