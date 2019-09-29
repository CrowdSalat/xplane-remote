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
import logging
import os
import socket
import struct
import sys
import time

DREF_OVERRIDE = b"sim/operation/override/override_planepath\0"
DREF_X = b'sim/flightmodel/position/local_x\0'                        # double	y	meters	The location of the plane in OpenGL coordinates                             
DREF_Y = b'sim/flightmodel/position/local_y\0'                        # double	y	meters	The location of the plane in OpenGL coordinates         
DREF_Z = b'sim/flightmodel/position/local_z\0'                        # double	y	meters	The location of the plane in OpenGL coordinates
DREF_MISSN_TIME = b'sim/time/total_flight_time_sec\0'                 # float	y	seconds	Total time since the flight got reset by something

DREF_AP_ACTIVATE = b'sim/cockpit/autopilot/autopilot_mode\0' # 2.0 is on
DREF_AP_SET_ALTI_IN_FTMSL = b'sim/cockpit/autopilot/altitude\0' #float	y	ftmsl	Altitude dialed into the AP
DREF_AP_SET_VV_IN_FPM = b'sim/cockpit/autopilot/vertical_velocity\0'
DREF_AP_HEADING_LEVEL = b'sim/cockpit/autopilot/heading_roll_mode\0' # Bank limit - 0 = auto, 1-6 = 5-30 degrees of bank
DREF_AP_HEADING_IN_DEGREE = b'sim/cockpit/autopilot/heading_mag\0' # 	float	y	degm	The heading to fly (magnetic, preferred) pilot
    
# Toggles AP MODE Buttons
# http://www.xsquawkbox.net/xpsdk/mediawiki/Sim/cockpit/autopilot/autopilot_state
# 16  VVI Climb Engage Toggle 
# 2   Heading Hold Engage
DREF_AP_STATE_TOGGLE_FLAG = b'sim/cockpit/autopilot/autopilot_state\0'


ip = "192.168.23.192"
port = 49000
HEADER_DREF = b"DREF\0"
HEADER_RREF = b"RREF\0"

logger = logging.getLogger('xplane_remote')

SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dref_dict = {}
dref_list= []

def set_position_x():
     '''
     nutzt offset. Jedoch gibt es scheinbar immer feste Grenzen an denen der longitude Wert hängen bleibt.
     '''
     value_override = 1
     dref_override = add_filler_bytes(DREF_OVERRIDE)
     msgLocalX = HEADER_DREF + struct.pack('f', value_override) + dref_override
     send_message(msgLocalX)

     value_x_offset = -100
     stringLocalX = add_filler_bytes(DREF_X)
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



def set_dref(dref_name, dref_value):
     msgLocalX = HEADER_DREF + struct.pack('f', dref_value)+ add_filler_bytes(dref_name)
     send_message(msgLocalX)

def get_dreafs():
     read_rref()
     return dref_dict

def get_dreaf(dref_name):
     if dref_name not in dref_dict:
          send_rref(dref_name)
     read_rref()
     return dref_dict.get(dref_name)

def send_rref(dref_name, freq=1):
     new_index = len(dref_list) # index for the additional field
     dref_freq = struct.pack('i', freq)
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
     if MESSAGE_LEN % MESSAGE_OFFSET != 0:
          logger.error('message lenght {} is not multiple of offset lenght {}. Therefor the decoding of the structs probably went wrong.'.format(MESSAGE_LEN,MESSAGE_OFFSET))
     MESSAGES_NR = int(MESSAGE_LEN / MESSAGE_OFFSET)

     header = data[0:HEADER_LEN]
     for i in range(0,MESSAGES_NR):
          offset_index = HEADER_LEN + (MESSAGE_OFFSET * i)   
          offset_value = offset_index + FIELD_LEN
          index = struct.unpack('<i', data[offset_index:offset_index + FIELD_LEN])[0]
          value =  struct.unpack('<f', data[offset_value:offset_value + FIELD_LEN])[0]
          
          logger.info('%s, %s, %s',str(index), str(value), str(dref_list[index]))
          dref_dict[dref_list[index]] = value

def config_logger():
     logger.setLevel(logging.INFO)
     
     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
     
     ch = logging.StreamHandler()
     ch.setFormatter(formatter)

     script_path = os.path.dirname(sys.argv[0])
     fh = logging.FileHandler(os.path.join(script_path,'python_remote.log'), encoding='utf-8')
     fh.setFormatter(formatter)

     logger.addHandler(ch)


if __name__ == "__main__":
     config_logger()

     get_dreaf(DREF_X) 
     get_dreaf(DREF_Y) 
     get_dreaf(DREF_Z) 
     get_dreaf(DREF_MISSN_TIME)
     
     logger.info(get_dreafs())
     
     set_dref(DREF_AP_ACTIVATE, 2.0)

     # climb and sink
     set_dref(DREF_AP_SET_ALTI_IN_FTMSL, 4500.0)
     set_dref(DREF_AP_STATE_TOGGLE_FLAG, 16.0) 
     set_dref(DREF_AP_SET_VV_IN_FPM, -200.0)
     
     input('click')
     #reset time
     set_dref(DREF_MISSN_TIME, 0.0)
     

     # banks
     set_dref(DREF_AP_STATE_TOGGLE_FLAG, 2.0) #   Heading Hold Engage 
     set_dref(DREF_AP_HEADING_LEVEL, 6.0) # wie starke kurven im hdg mode: 1-6 for 5-30 degree
     set_dref(DREF_AP_HEADING_IN_DEGREE, 350.0)  
