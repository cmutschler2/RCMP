# Receive the file

import argparse
import socket
from pathlib import Path

MSG_SIZE = 1000
try:
    parser = argparse.ArgumentParser(description="An RCMP File recipient")

    parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                        help="UDP port the server is listening on (default 12345)")
    parser.add_argument("-f", "--file", dest="filename", default="",
                        help="destination file name for incoming transmission (default='')")
                        #Should this have a default -- doesn't quite make sense & it exits fine w/o
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
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        ip_address = getNetworkIp()
        print("Socket opening at %s on port" % ip_address, args.port)
        addr = ( ip_address, args.port )

        file_socket.bind(addr)

    except Exception as e:
        print("Error: %s" % e)
        exit(-1)

    if Path(args.filename).is_file():
        usr_input = input("File aready exists. Overwrite? (y/N): ")
        if usr_input!='y' and usr_input!='Y':
            exit(-1)

    with open(args.filename, "wb") as f:
        while True:
            msg, sdAddr = file_socket.recvfrom(MSG_SIZE)
            if args.verbose:
                print("Datagram received of size %d" % len(msg))
            datagram = msg[12:] # Skip header for now
            f.write(msg)
            file_socket.sendto( bytes("ACK".encode("utf-8")), sdAddr)
            if args.verbose:
                print("ACK")
            if len(msg) < 1000:
                break
    file_socket.close()
except KeyboardInterrupt as e:
    print("caught KeyboardInterrupt")

