# Send file

import argparse
import socket
from random import randbytes # is random ~= to unique?
import os

MSG_SIZE = 1000
ACK_SIZE = 8
HEADER_SIZE = 13
ACK_PKT = 1
NO_ACK_PKT = 0
DEBUG = False;

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
    nextAckPkt = 0;
    ackGap = 1;

    def getNetworkIp(): # is this fn necessary (in this file)?
        '''This is just a way to get the IP address of interface this program is
        communicating over.'''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]

    def getByteArray(data, commId, fileBytes, packetNum, ackPkt): 
        ''' Way to abstract the task of creating Header + data message to send 
        over socket '''
        fileBytes_bytes = fileBytes.to_bytes(4, 'big')
        packetNum_bytes = packetNum.to_bytes(4, 'big')
        ackPkt_bytes = ackPkt.to_bytes(1, 'big')
        # join() needs arg as iterable with > 1 elem (use empty bytes, b'')
        total_byte = commId.join([b'', fileBytes_bytes]) 
        total_byte = total_byte.join([b'', packetNum_bytes])
        total_byte = total_byte.join([b'', ackPkt_bytes])
        total_byte = total_byte.join([b'', data])
        return total_byte

    try:
        print("Opening socket on port %d" % args.port)
        file_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
    except Exception as e:
        print("Error occured during connection process: %s" % e)
        exit(1)

    try:
        with open(args.filename, "rb") as f:  
            # Find full file size? = os lib might have a better method
            f.seek(0, os.SEEK_END)
            fileSize = f.tell() # get full size of file
            f.seek(0, 0) # reset to end

            data = f.read(MSG_SIZE) 
            while len(data)==MSG_SIZE: 
                if args.verbose:
                    print("*"*36 + "Sent Msg" + '*'*36)
                    print("DEBUG: Bytes read from file: %d" % len(data))

                if packetNum == nextAckPkt:
                    datagram = getByteArray(data, communicationId, fileSize, packetNum, ACK_PKT)
                else:
                    datagram = getByteArray(data, communicationId, fileSize, packetNum, NO_ACK_PKT)

                if args.verbose: 
                    print("DEBUG: Bytes of message sent: %d" % len(datagram))
                    print("TotalPkt: ", datagram)
                    print("\tcommId: ", datagram[0:4])
                    print("\tfileBytes: ", datagram[4:8], " (as Int: %d)" % fileSize)
                    print("\tpacketNum: ", datagram[8:12], " (as Int: %d)" % packetNum)
                    print("\tackPkt?: ", datagram[12:13])
                    print("\tpayload: ", datagram[13:])

                file_socket.sendto( datagram, (args.ip_address,args.port) )

                if packetNum == nextAckPkt:
                    ackMsg, rcAddr = file_socket.recvfrom(ACK_SIZE)
                    print("*"*36 + "Recv Ack" + '*'*36)
                    print("TotalPkt", ackMsg)
                    print("\tcommId: ", ackMsg[0:4])
                    print("\tpacketNum: ", ackMsg[4:8], " (as Int: %d)" % int.from_bytes(ackMsg[4:8], "big") )
                    nextAckPkt+=ackGap
                    ackGap+=1

                packetNum+=1
                data = f.read(MSG_SIZE)
            if args.verbose:
                print("*"*36 + "Sent Msg" + '*'*36)
                print("DEBUG: Bytes read from file: %d" % len(data))
            datagram = getByteArray(data, communicationId, fileSize, packetNum, ACK_PKT)
            if args.verbose: 
                print("DEBUG: Bytes of message sent: %d" % len(datagram))
                print("TotalPkt: ", datagram)
                print("\tcommId: ", datagram[0:4])
                print("\tfileBytes: ", datagram[4:8], " (as Int: %d)" % fileSize)
                print("\tpacketNum: ", datagram[8:12], " (as Int: %d)" % packetNum)
                print("\tackPkt?: ", datagram[12:13])
                print("\tpayload: ", datagram[13:])

            file_socket.sendto( datagram, (args.ip_address,args.port) )
        file_socket.close()
    except FileNotFoundError:
        print("Error: File does not exist.")
except KeyboardInterrupt:
    print("caught KeyboardInterrupt")

