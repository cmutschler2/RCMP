# Send file

import argparse
import socket
import mimetypes
import sys

MSG_SIZE = 1000
ACK_SIZE = 3

try:
    parser = argparse.ArgumentParser(description="An RCMP File sender")

    parser.add_argument("-i", "--ip_address", dest="ip_address", default="localhost",
                        help="server hostname or IP address (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                        help="TCP port the server is listening on (default 12345)")
    parser.add_argument("-f", "--file", dest="filename", default=None,
                        help="source file name to transmit (default=None)")
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

    try:
        print("Opening socket on port %d" % args.port)
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    except Exception as e:
        print("Error occured during connection process: %s" % e)
        exit(1)

    try:
        with open(args.filename, "rb") as f:
            data = f.read(MSG_SIZE)
            while len(data)==MSG_SIZE:
                if args.verbose:
                    print("DEBUG: Bytes read from file: %d" % len(data))
                file_socket.sendto( data, (args.ip_address,args.port) )
                msg, rcAddr = file_socket.recvfrom(ACK_SIZE)
                if msg.decode() == "ACK":
                    if args.verbose:
                        print("ACK received.")
                    data = f.read(MSG_SIZE)
            if args.verbose:
                print("DEBUG: Bytes read from file: %d" % len(data))
            file_socket.sendto( data, (args.ip_address,args.port) )
        file_socket.close()
    except FileNotFoundError:
        print("Error: File does not exist.")
except KeyboardInterrupt:
    print("aught KeyboardInterrupt")