"""

Struktur DREF Schreibend:
'RREF0\' + 
struct dref_struct
{
     xflt var;
     xchr dref_path[500];
};
TODO:
für var wird immer das struct modul verwendet
für dref_path nicht... sollte wohl also generell ohne struct fungkionieren. 
Struct möglicherweise nur für floats relevant?

TODO's
Test neue Methoden
mission_time
datarefs im menü aktivieren?

Erkenntnis:
set_longi_lati_coordinates tut nichts, die Anzeigen im Cockpit spinnen aber danach

"""

import socket
import time
import struct
import math
import numpy as np
import array as arr

ip = "192.168.23.192"
port = 49000
header = b"DREF\0"


def set_position_x():
     '''
     nutzt offset. Jedoch gibt es scheinbar immer feste Grenzen an denen der longitude Wert hängen bleibt.
     '''
     value_override = 1
     dref_override = add_filler_bytes(b"sim/operation/override/override_planepath\0")
     msgLocalX = header + struct.pack('f', value_override) + dref_override
     send_message(msgLocalX)

     value_x_offset = -100
     stringLocalX = add_filler_bytes(b"sim/flightmodel/position/local_x\0")
     msgLocalX = header + struct.pack('f', value_x_offset)+ stringLocalX
     send_message(msgLocalX)

def add_filler_bytes(dref_name: bytes) -> bytes:
     xplane_dref_expected_byte_lenght = 500
     return dref_name + ((xplane_dref_expected_byte_lenght - len(dref_name)) * b' ')

def send_message(byte_message):
     outsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
     outsock.sendto(byte_message, (ip, port))
     outsock.close()   

def set_altitude(altitude=1000.0):
     '''
     Klappt nicht. Flugzeug wird crasht direkt
     '''
#     altitude_dref = add_filler_bytes(b'sim/flightmodel/position/elevation\0')
     altitude_dref = add_filler_bytes(b'sim/flightmodel/position/local_z\0')

     altitude_value = altitude
     msg =  header + struct.pack('f', altitude_value) + altitude_dref
     send_message(msg)

def set_longi_lati_coordinates(x=50.941357, y=6.958307):
     '''
     Passiert nichts. Alerdings sah das Cockpit nach dem Stezen nicht ganz korrekt aus.
     '''
     x_dref = add_filler_bytes(b'sim/flightmodel/position/longitude\0')
     msg =  header + struct.pack('f', x) + x_dref
     send_message(msg)

     y_dref = add_filler_bytes(b'sim/flightmodel/position/latitude\0')
     msg =  header + struct.pack('f', y) + y_dref
     send_message(msg)


if __name__ == "__main__":
     set_position_x()
     
     #set_altitude(2001)

     #set_longi_lati_coordinates()