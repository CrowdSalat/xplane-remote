import socket
import time
import struct
import math
import numpy as np
import array as arr

ip = "192.168.23.192"
port = 49000

def set_position_x():
     outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     
     header = b"DREF\0"
     value_override = 1
     dref_override = add_filler_bytes(b"sim/operation/override/override_planepath\0")
     msgLocalX = header + struct.pack('f', value_override) + dref_override
     outsock.sendto(msgLocalX, (ip, port))

     value_x_offset = 1
     stringLocalX = add_filler_bytes(b"sim/flightmodel/position/local_x\0")
     msgLocalX = header + struct.pack('f', value_x_offset)+ stringLocalX
     outsock.sendto(msgLocalX, (ip, port))


def add_filler_bytes(dref_name):
     xplane_dref_expected_byte_lenght = 500
     return dref_name + ((xplane_dref_expected_byte_lenght - len(dref_name)) * b' ')
     
      

if __name__ == "__main__":
     set_position_x()