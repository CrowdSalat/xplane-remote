import socket
import struct

refs = {}

def DecodeDataMessage(message):
    # Message consists of 4 byte type and 8 times a 4byte float value.
    # Write the results in a python dict.
    values = {}
    typelen = 4
    type = int.from_bytes(message[0:typelen], byteorder='little')
    data = message[typelen:]
    dataFLOATS = struct.unpack("<ffffffff",data)
    if type == 0:
        values["fps"]=dataFLOATS[0]
    elif type == 1:
        values["real_time"]=dataFLOATS[0]
        values["mission_time"]=dataFLOATS[2]
    else:
        print("  Type ", type, " not implemented: ",dataFLOATS)
    return values

def DecodePacket(data):
    # Packet consists of 5 byte header and multiple messages.
    valuesout = {}
    headerlen = 5
    header = data[0:headerlen]
    messages = data[headerlen:9]
    if(header==b'DREF+'):
        '''
        you receive:
        DREF+
        struct dref_struct_out
        {
            xflt dref_flt;
        };
        sim.....
        '''
        simname = str(data[9:50])

        value = struct.unpack('<f', data[5:9])[0]
        refs[simname] = value
    else:
        print("Packet type not implemented. ")
        print("  Header: ", header)
        print("  Data: ", messages)
    return valuesout

def main():
    # Open a Socket on UDP Port X
    UDP_IP = ""
    UDP_PORT = 59080
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    print('Socket is open on Listing on %s:%s', UDP_IP, UDP_PORT)
    for i in range(0,20):
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        #print('received data from ' + str(addr))
        DecodePacket(data)

    for x in refs:
        type
        print(x + ' ' + str(refs[x]))
    #print(repr(data))
    

if __name__ == '__main__':
    print('Start program')
    main()
