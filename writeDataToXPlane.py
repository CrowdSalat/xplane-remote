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
import atexit

logger = logging.getLogger('xplane_remote')

# DREF API Names 
DREF_OVERRIDE = b"sim/operation/override/override_planepath\0"
DREF_X = b'sim/flightmodel/position/local_x\0'                        # double	y	meters	The location of the plane in OpenGL coordinates                             
DREF_Y = b'sim/flightmodel/position/local_y\0'                        # double	y	meters	The location of the plane in OpenGL coordinates         
DREF_Z = b'sim/flightmodel/position/local_z\0'                        # double	y	meters	The location of the plane in OpenGL coordinates
DREF_MISSN_TIME = b'sim/time/total_flight_time_sec\0'                 # float	y	seconds	Total time since the flight got reset by something
DREF_INDICATOR_ALTI = b'sim/cockpit2/gauges/indicators/radio_altimeter_height_ft_pilot\0' #float	900+	no	feet	Radio-altimeter indicated height in feet, pilot-side
DREF_INDICATOR_HEADING = b'sim/cockpit2/gauges/indicators/compass_heading_deg_mag\0'	     #float	n	degrees_magnetic	Indicated heading of the wet compass, in degrees.


DREF_AP_ACTIVATE = b'sim/cockpit/autopilot/autopilot_mode\0'          # 2.0 is on

DREF_AP_SET_ALTI_IN_FTMSL = b'sim/cockpit/autopilot/altitude\0'       #float	y	ftmsl	Altitude dialed into the AP
DREF_AP_SET_ALTI_IN_FTMSL2 = b'sim/cockpit2/autopilot/altitude_hold_ft\0'	#float	n	feet	Altitude hold commanded in feet indicated.
DREF_AP_SET_VV_IN_FPM = b'sim/cockpit/autopilot/vertical_velocity\0'
DREF_AP_SET_VV_IN_FPM2 = 'sim/cockpit2/autopilot/vvi_dial_fpm\0'	     #float	y	feet/minute	VVI commanded in FPM.
DREF_AP_SET_HEADING_LEVEL = b'sim/cockpit/autopilot/heading_roll_mode\0'  # Bank limit - 0 = auto, 1-6 = 5-30 degrees of bank
DREF_AP_SET_HEADING_LEVEL2 = b'sim/cockpit2/autopilot/bank_angle_mode\0'	#int	y	enum	Maximum bank angle mode, 0->6. Higher number is steeper allowable bank.
DREF_AP_SET_HEADING_IN_DEGREE = b'sim/cockpit/autopilot/heading_mag\0'    # 	float	y	degm	The heading to fly (magnetic, preferred) pilot
DREF_AP_SET_HEADING_IN_DEGREE2 = b'sim/cockpit2/autopilot/heading_dial_deg_mag_pilot\0'	#float	y	degrees_magnetic	Heading hold commanded, in degrees magnetic.


DREF_AP_MODE_HEADING_STATUS = 'sim/cockpit2/autopilot/heading_mode\0'# int	900+	no	enum	Autopilot heading mode.
DREF_AP_MODE_ALTITUDE_STATUS = 'sim/cockpit2/autopilot/altitude_mode\0'#int	900+	no	enum	Autopilot altitude mode.
# Toggles AP MODE Buttons
# http://www.xsquawkbox.net/xpsdk/mediawiki/Sim/cockpit/autopilot/autopilot_state
# 16  VVI Climb Engage Toggle 
# 2   Heading Hold Engage
DREF_AP_STATE_TOGGLE_FLAG = b'sim/cockpit/autopilot/autopilot_state\0'


HEADER_DREF = b"DREF\0"
HEADER_RREF = b"RREF\0"

# Connection
IP = "192.168.23.192"
PORT = 49000
SOCKET = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
SOCKET.setblocking(0)

# save state of requested rref fields
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

def send_message(byte_message:bytes):
     SOCKET.sendto(byte_message, (IP, PORT))

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

def send_rref(dref_name, freq=2):
     new_index = len(dref_list) # index for the additional field
     dref_freq = struct.pack('i', freq)
     dref_en = struct.pack('i', new_index)
     dref_value = add_filler_bytes(dref_name, 400)
     msg = HEADER_RREF + dref_freq  + dref_en + dref_value
     send_message(msg)
     dref_list.append(dref_name) # add the new field to the list of read drefs

def request_refs(freq=2):
     dref_list.append(DREF_INDICATOR_ALTI)
     dref_list.append(DREF_INDICATOR_HEADING)

     dref_freq = struct.pack('i', freq)
     for i, val in enumerate(dref_list):
          dref_en = struct.pack('i', new_index)
          dref_value = add_filler_bytes(dref_name, 400)



def read_rref():
     data, addr = SOCKET.recvfrom(1024)
     DATA_LEN = len(data)
     # TODO wenn hier error einfach erstmal funktion abbrechen und alte werte im dict behalten
     HEADER_LEN = 5
     MESSAGE_OFFSET = 8
     MESSAGE_LEN = DATA_LEN - HEADER_LEN
     FIELD_LEN = int(MESSAGE_OFFSET/2)
     
     if MESSAGE_LEN % MESSAGE_OFFSET != 0:
          logger.error('message lenght {} is not multiple of offset lenght {}. Therefor the decoding of the structs probably went wrong.'.format(MESSAGE_LEN,MESSAGE_OFFSET))
     MESSAGES_NR = int(MESSAGE_LEN / MESSAGE_OFFSET)
     if MESSAGES_NR != len(dref_list):
          logger.warn('expected {} structs but received {}'.format(len(dref_list),MESSAGES_NR))

     for i in range(0,MESSAGES_NR):
          offset_index = HEADER_LEN + (MESSAGE_OFFSET * i)   
          offset_value = offset_index + FIELD_LEN
          index = struct.unpack('<i', data[offset_index:offset_index + FIELD_LEN])[0]
          value =  struct.unpack('<f', data[offset_value:offset_value + FIELD_LEN])[0]
          dref_dict[dref_list[index]] = value

def config_logger():
     logger.setLevel(logging.DEBUG)
     
     formatter = logging.Formatter('%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')
     
     ch = logging.StreamHandler()
     ch.setFormatter(formatter)

     script_path = os.path.dirname(sys.argv[0])
     fh = logging.FileHandler(os.path.join(script_path,'python_remote.log'), encoding='utf-8')
     fh.setFormatter(formatter)

     logger.addHandler(ch)
     logger.addHandler(fh)

#TODO is untested
def end_rref():
     for dref_name in dref_list:
          send_rref(dref_name,freq=0)

#TODO is untested
def close_connections():
     #TODO shutdown?
     #SOCKET.close()
     print('TBD')



def fly_banks():
     set_dref(DREF_AP_STATE_TOGGLE_FLAG, 2.0) #   Heading Hold Engage 
     set_dref(DREF_AP_SET_HEADING_LEVEL, 6.0) # wie starke kurven im hdg mode: 1-6 for 5-30 degree
     set_dref(DREF_AP_SET_HEADING_IN_DEGREE, 350.0)

def rst_msn_time():
     set_dref(DREF_MISSN_TIME, 0.0)

def fly_parable():
     set_dref(DREF_AP_ACTIVATE, 2.0)

     start_alt = 1500.0
     altitude = 200.0
     fpm = 200.0

     climb_to(start_alt, fpm)
     wait_until_altitude_reached(altitude, reset_time=True)

     climb(altitude, fpm)
     wait_until_altitude_reached(altitude)
     rst_msn_time()

     climb(-altitude, -fpm)


# 0 values?

def climb_to(altitude_target:float, fpm:float):
     logger.info('climb to {} with speed {}'.format(altitude_target, fpm))
     current_altitude = get_dreaf(DREF_INDICATOR_ALTI) # TODO  called twice if called by climb function
     altitude_delta = altitude_target - current_altitude 
     if ((altitude_delta < 0) != (fpm < 0)): # both negativ or positiv 
          logger.warn('incosistent use of climb method. Altitude_delta {}, fpm{}'.format(altitude_delta, fpm))
          return None

     set_dref(DREF_AP_SET_ALTI_IN_FTMSL, altitude_target)
     # TODO is toggle? than create an activate function
     set_dref(DREF_AP_STATE_TOGGLE_FLAG, 16.0) # VVI Climb Engage Toggle 
     set_dref(DREF_AP_SET_VV_IN_FPM, fpm)


def climb(altitude_delta:float, fpm:float):
     logger.info('climb {} with speed {}'.format(altitude_delta, fpm))
     current_altitude = get_dreaf(DREF_INDICATOR_ALTI)
     altitude_target = current_altitude + altitude_delta
     climb_to(altitude_target, fpm)
     



def wait_until_altitude_reached(expected_altitude, reset_time=False):
     '''
     Checks if altitude is reached. If not waits 0.5 seconds and check again.
     '''
     altitude_not_reached = True
     while altitude_not_reached:
          current_altitude = get_dreaf(DREF_INDICATOR_ALTI)
          altitude_delta = expected_altitude - current_altitude
          if abs(altitude_delta) < 50.0:
               altitude_not_reached = False 
          if reset_time:
               rst_msn_time()
          time.sleep(0.5)



def xp_config_enviroment():
     '''
     config weather etc.
     '''
     print('-------TODO---------')



# 
atexit.register(end_rref)

if __name__ == "__main__":
     try:
          config_logger()

          logger.info(get_dreaf(DREF_X))
          logger.info(get_dreaf(DREF_Y) )
          logger.info(get_dreaf(DREF_Z) )
          logger.info(get_dreaf(DREF_MISSN_TIME))
          
          logger.info(get_dreafs())

          set_dref(DREF_AP_ACTIVATE, 2.0)

          xp_config_enviroment()

          #TODO reset fuel
          # climb and sink
          #fly_parable()
          
          #reset time
          rst_msn_time()          

          # banks
          #fly_banks()
     finally:
          end_rref()
          close_connections() 


