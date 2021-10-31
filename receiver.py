################################################################################
# Course: cs 332
# Project: RCMP
# File: Receiver.py
# Names: Christian Mutschler, Kris Miedema
# Date: 10/31/21
################################################################################
import argparse
import socket
from pathlib import Path

MSG_SIZE = 1000
HEADER_SIZE = 13
ACK_SIZE = 8
try:
    parser = argparse.ArgumentParser(description="An RCMP File recipient")

    parser.add_argument("-p", "--port", dest="port", type=int, default=12345,
                        help="UDP port the server is listening on (default 12345)")
    parser.add_argument("-f", "--file", dest="filename", default="",
                        help="destination file name for incoming transmission (default='')")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                        help="turn verbose output on")
    args = parser.parse_args()

    # Header Values
    expPktNum = 0;

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

    try:
        with open(args.filename, "wb") as f:
            while True:
                msg, sdAddr = file_socket.recvfrom(MSG_SIZE + HEADER_SIZE)

                if args.verbose:
                    print("*"*36 + "Recv Msg" + '*'*36)
                    print("Datagram received of size %d" % len(msg))
                    print("TotalPkt: ", msg)
                    print("\tcommId: ", msg[0:4])
                    print("\tfileBytes: ", msg[4:8], " (as Int: %d)" % int.from_bytes(msg[4:8], "big") )
                    print("\tpacketNum: ", msg[8:12], " (as Int: %d)" % int.from_bytes(msg[8:12], "big") )
                    print("\tackPkt?: ", msg[12:13])
                    print("\tpayload: ", msg[13:])

                # this will need to be protected for missing packet
                fileData = msg[13:] # Skip header for now
                f.write(fileData) 

                # It would be great to find a python way of not having all the numbers set here
                # if next packet is the expected one
                expPkt_bytes = expPktNum.to_bytes(4, 'big')
                if(msg[8:12] == expPkt_bytes):
                    expPktNum+=1 
                    # if it is marked to be acked - send ack
                    if(int.from_bytes(msg[12:13], "big")):
                        ackMsg = msg[0:4].join([b'', expPkt_bytes]) # msg[0:4] is the commId (do we check if this is equal)
                        file_socket.sendto( ackMsg, sdAddr)

                if args.verbose:
                    print("*"*36 + "Sent Ack" + '*'*36)
                    print("TotalPkt", ackMsg)
                    print("\tcommId: ", ackMsg[0:4])
                    print("\tpacketNum: ", ackMsg[4:8], " (as Int: %d)" % int.from_bytes(ackMsg[4:8], "big") )

                if len(msg) < (MSG_SIZE+HEADER_SIZE): # What happens if we have exact mult?
                    break
    except FileNotFoundError:
        print("Error: File does not exist.")
   
    file_socket.close()
except KeyboardInterrupt as e:
    print("caught KeyboardInterrupt")

