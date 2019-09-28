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
HEADER_DREF = b"DREF\0"
HEADER_RREF = b"RREF\0"

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dref_dict = {}
dref_list= []

def set_position_x():
     '''
     nutzt offset. Jedoch gibt es scheinbar immer feste Grenzen an denen der longitude Wert hängen bleibt.
     '''
     value_override = 1
     dref_override = add_filler_bytes(b"sim/operation/override/override_planepath\0")
     msgLocalX = HEADER_DREF + struct.pack('f', value_override) + dref_override
     send_message(msgLocalX)

     value_x_offset = -100
     stringLocalX = add_filler_bytes(b"sim/flightmodel/position/local_x\0")
     msgLocalX = HEADER_DREF + struct.pack('f', value_x_offset)+ stringLocalX
     send_message(msgLocalX)

def add_filler_bytes(dref_name: bytes, xplane_dref_expected_byte_lenght = 500) -> bytes:
     return dref_name + ((xplane_dref_expected_byte_lenght - len(dref_name)) * b' ')

def send_message(byte_message):
     SOCKET.sendto(byte_message, (ip, port))

def set_altitude(altitude=1000.0):
     '''
     Klappt nicht. Flugzeug wird crasht direkt
     '''
#     altitude_dref = add_filler_bytes(b'sim/flightmodel/position/elevation\0')
     altitude_dref = add_filler_bytes(b'sim/flightmodel/position/local_z\0')

     altitude_value = altitude
     msg =  HEADER_DREF + struct.pack('f', altitude_value) + altitude_dref
     send_message(msg)

def set_longi_lati_coordinates(x=50.941357, y=6.958307):
     '''
     Passiert nichts. Alerdings sah das Cockpit nach dem Stezen nicht ganz korrekt aus.
     '''
     x_dref = add_filler_bytes(b'sim/flightmodel/position/longitude\0')
     msg =  HEADER_DREF + struct.pack('f', x) + x_dref
     send_message(msg)

     y_dref = add_filler_bytes(b'sim/flightmodel/position/latitude\0')
     msg =  HEADER_DREF + struct.pack('f', y) + y_dref
     send_message(msg)


def read_datarefs():
     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

     #activate
     drefs = []
     drefs.append(b'sim/flightmodel/position/true_airspeed\0') # float	n	meters/sec	Air speed true - this does not take into account air density at altitude!
     drefs.append(b'sim/flightmodel/position/local_x\0') # double	y	meters	The location of the plane in OpenGL coordinates
     drefs.append(b'sim/flightmodel/position/local_y\0') # double	y	meters	The location of the plane in OpenGL coordinates
     drefs.append(b'sim/flightmodel/position/local_z\0') # double	y	meters	The location of the plane in OpenGL coordinates
     drefs.append(b'sim/time/total_flight_time_sec\0') # float	y	seconds	Total time since the flight got reset by something



     dref_freq = struct.pack('i', 1)
     for i in range(0, len(drefs)):
          dref_en = struct.pack('i', i)
          dref_value = add_filler_bytes(drefs[i], 400)
          msg = HEADER_RREF + dref_freq  + dref_en + dref_value
          sock.sendto(msg, (ip, port))
          


     #read
     print('receive')
     data, addr = sock.recvfrom(1024)
     print('received from ' + str(addr))
     print('data ' + str(data))
     data_lenght = len(data)
     print('data lenght ' + str(data_lenght))

     HEADER_LEN = 5
     header = data[0:HEADER_LEN]
     nr_msgs = len(drefs)
     msg = data[5: len(data)]
     data.strip()
     print('message lenght: ' + str(data_lenght - HEADER_LEN) )
     for i in range(0,nr_msgs):
          offset = 4
          start_index = HEADER_LEN + (offset * 2 * i)   
          value_index = start_index + offset
          index = struct.unpack('<i', data[start_index:start_index + offset])[0]
          value =  struct.unpack('<f', data[value_index:value_index + offset])[0]
          print(header,index, value, drefs[i])
     
     
     # deactivate
     dref_freq = struct.pack('i', 0)
     for i in range(0, len(drefs)):
          dref_en = struct.pack('i', i)
          dref_value = add_filler_bytes(drefs[i], 400)
          msg = HEADER_RREF + dref_freq  + dref_en + dref_value
          sock.sendto(msg, (ip, port))
     sock.close() 


def set_dref(dref_name, dref_value):
     msgLocalX = HEADER_DREF + struct.pack('f', dref_value)+ add_filler_bytes(dref_name)
     send_message(msgLocalX)


def get_dreaf(dref_name):
     if dref_name not in dref_dict:
          send_rref(dref_name)
     read_rref()
     return dref_dict.get(dref_name)

def send_rref(dref_name):
     new_index = len(dref_list) # index for the additional field
     dref_freq = struct.pack('i', 1)
     dref_en = struct.pack('i', new_index)
     dref_value = add_filler_bytes(dref_name, 400)
     msg = HEADER_RREF + dref_freq  + dref_en + dref_value
     SOCKET.sendto(msg, (ip, port))
     dref_list.append(dref_name) # add the new field to the list of read drefs


def read_rref():
     data, addr = SOCKET.recvfrom(1024)
     
     DATA_LEN = len(data)
     
     HEADER_LEN = 5
     MESSAGE_OFFSET = 8
     MESSAGE_LEN = DATA_LEN - HEADER_LEN
     FIELD_LEN = int(MESSAGE_OFFSET/2)
     print('data lenght ' + str(DATA_LEN))
     print('message lenght: ' + str(MESSAGE_LEN) )
     print('message is multiple of ME_OFFSET: ' + str(MESSAGE_LEN % MESSAGE_OFFSET == 0) )
     MESSAGES_NR = int(MESSAGE_LEN / MESSAGE_OFFSET)

     header = data[0:HEADER_LEN]
     for i in range(0,MESSAGES_NR):
          offset_index = HEADER_LEN + (MESSAGE_OFFSET * i)   
          offset_value = offset_index + FIELD_LEN
          index = struct.unpack('<i', data[offset_index:offset_index + FIELD_LEN])[0]
          value =  struct.unpack('<f', data[offset_value:offset_value + FIELD_LEN])[0]
          
          print(header,index, value, dref_list[index])
          dref_dict[dref_list[index]] = value


if __name__ == "__main__":
     #set_position_x()
     print(get_dreaf(b'sim/flightmodel/position/true_airspeed\0'))
     print(get_dreaf(b'sim/time/total_flight_time_sec\0'))

     print(dref_dict)

     #set_altitude(2001)

     #set_longi_lati_coordinates()
     #read_datarefs()

     set_dref(b'sim/cockpit/autopilot/autopilot_mode\0', 2.0)
     
     # climb and sink
     #set_dref(b'sim/cockpit/autopilot/altitude\0', 4500.0)
     #set_dref(b'sim/cockpit/autopilot/autopilot_state\0', 16.0) #  VVI Climb Engage Toggle # http://www.xsquawkbox.net/xpsdk/mediawiki/Sim/cockpit/autopilot/autopilot_state
     #set_dref(b'sim/cockpit/autopilot/vertical_velocity\0', -200.0)
     
     #reset time
     set_dref(b'sim/time/total_flight_time_sec\0', 0.0)
     

     # banks
     
     #set_dref(b'sim/cockpit/autopilot/autopilot_state\0', 2.0) #   Heading Hold Engage 
     #set_dref(b'sim/cockpit/autopilot/heading_roll_mode\0', 6.0) # wie starke kurven im hdg mode: 1-6 for 5-30 degree
     #set_dref(b'sim/cockpit/autopilot/heading_mag\0', 350.0)  

