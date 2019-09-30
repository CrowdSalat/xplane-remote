import pyxpudpserver as XPUDP
import logging
import os
import socket
import struct
import sys
import time
import atexit

logger = logging.getLogger('xplane_remote')

# DREF API Names 
DREF_OVERRIDE = 'sim/operation/override/override_planepath'
DREF_X = 'sim/flightmodel/position/local_x'                        # double	y	meters	The location of the plane in OpenGL coordinates                             
DREF_Y = 'sim/flightmodel/position/local_y'                        # double	y	meters	The location of the plane in OpenGL coordinates         
DREF_Z = 'sim/flightmodel/position/local_z'                        # double	y	meters	The location of the plane in OpenGL coordinates
DREF_MISSN_TIME = 'sim/time/total_flight_time_sec'                 # float	y	seconds	Total time since the flight got reset by something
DREF_INDICATOR_ALTI = 'sim/cockpit2/gauges/indicators/altitude_ft_pilot' #float	n	feet	Indicated height, MSL, in feet, primary system, based on pilots barometric pressure input.
DREF_INDICATOR_HEADING = 'sim/cockpit2/gauges/indicators/compass_heading_deg_mag'	     #float	n	degrees_magnetic	Indicated heading of the wet compass, in degrees.


DREF_AP_ACTIVATE = 'sim/cockpit/autopilot/autopilot_mode'          # 2.0 is on

DREF_AP_SET_ALTI_IN_FEET = 'sim/cockpit2/autopilot/altitude_dial_ft'	# float	y	feet	VVI commanded in FPM.
DREF_AP_SET_VV_IN_FPM = 'sim/cockpit/autopilot/vertical_velocity'
DREF_AP_SET_VV_IN_FPM2 = 'sim/cockpit2/autopilot/vvi_dial_fpm'	     #float	y	feet/minute	VVI commanded in FPM.
DREF_AP_SET_HEADING_LEVEL = 'sim/cockpit/autopilot/heading_roll_mode'  # Bank limit - 0 = auto, 1-6 = 5-30 degrees of bank
DREF_AP_SET_HEADING_LEVEL2 = 'sim/cockpit2/autopilot/bank_angle_mode'	#int	y	enum	Maximum bank angle mode, 0->6. Higher number is steeper allowable bank.
DREF_AP_SET_HEADING_IN_DEGREE = 'sim/cockpit/autopilot/heading_mag'    # 	float	y	degm	The heading to fly (magnetic, preferred) pilot
DREF_AP_SET_HEADING_IN_DEGREE2 = 'sim/cockpit2/autopilot/heading_dial_deg_mag_pilot'	#float	y	degrees_magnetic	Heading hold commanded, in degrees magnetic.


DREF_AP_MODE_HEADING_STATUS = 'sim/cockpit2/autopilot/heading_mode'# int	900+	no	enum	Autopilot heading mode.
DREF_AP_MODE_ALTITUDE_STATUS = 'sim/cockpit2/autopilot/altitude_mode'#int	900+	no	enum	Autopilot altitude mode.
# Toggles AP MODE Buttons
# http://www.xsquawkbox.net/xpsdk/mediawiki/Sim/cockpit/autopilot/autopilot_state
# 16  VVI Climb Engage Toggle 
# 2   Heading Hold Engage
DREF_AP_STATE_TOGGLE_FLAG = 'sim/cockpit/autopilot/autopilot_state'


def init_xp_remote():
     logger.info('Start Server.')
     XPUDP.pyXPUDPServer.initialiseUDP(('127.0.0.1',49008), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
     XPUDP.pyXPUDPServer.start() 
     logger.info('Server started.')

def close_xp_remote():
     logger.info('Shutdown Server.')
     XPUDP.pyXPUDPServer.quit()
     logger.info('Server shutdown.')

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



def set_planned_climbrate(fpm: float):
     set_dref(DREF_AP_SET_VV_IN_FPM2,fpm)



def fly_banks():
     #set_dref(DREF_AP_STATE_TOGGLE_FLAG, 2.0) #   Heading Hold Engage 
     #set_dref(DREF_AP_SET_HEADING_LEVEL, 6.0) # wie starke kurven im hdg mode: 1-6 for 5-30 degree
     #set_dref(DREF_AP_SET_HEADING_IN_DEGREE, 350.0)
     pass

def rst_msn_time():
     #set_dref(DREF_MISSN_TIME, 0.0)
     pass

def fly_parable():
     #set_dref(DREF_AP_ACTIVATE, 2.0)

     start_alt = 1500.0
     altitude = 200.0
     fpm = 200.0

     climb_to(start_alt, fpm)
     wait_until_altitude_reached(altitude, reset_time=True)

     climb(altitude, fpm)
     wait_until_altitude_reached(altitude)
     rst_msn_time()

     climb(-altitude, -fpm)

def climb_to(altitude_target:float, fpm:float):
     cur_alti = get_current_altitude()
     delta = altitude_target - cur_alti

     fpm = abs(fpm)
     if delta < 0:
          fpm *= -1

     set_planned_altitude(altitude_target)
     activate_mode_vs()
     set_planned_climbrate(fpm)

def activate_mode_vs(activate=True):
     activate_mode(16.0, 5, activate)

def activate_mode(mode:float, bit_pos:int ,activate=True):

     val = get_dref(DREF_AP_STATE_TOGGLE_FLAG)
     bit_flag = bin(int(val))
     bit_flag_reversed = bit_flag[::-1]
     bit = bit_flag_reversed[bit_pos- 1:bit_pos]
     if bit == '0' and activate:
          set_dref(DREF_AP_STATE_TOGGLE_FLAG, mode)
     elif bit == '1' and not activate:
          set_dref(DREF_AP_STATE_TOGGLE_FLAG, mode)
     else:
          pass # desired state is already reached


def climb(altitude_delta:float, fpm:float):
     current_altitude = get_current_altitude()
     altitude_target = current_altitude + altitude_delta
     climb_to(altitude_target, fpm)
          
def get_current_altitude():
     return get_dref(DREF_INDICATOR_ALTI)

def set_planned_altitude(target_altitude: float):
     set_dref(DREF_AP_SET_ALTI_IN_FEET,target_altitude)

def set_dref(dref_name, target_value, index= 0):
     XPUDP.pyXPUDPServer.sendXPDref(dref_name,index,target_value)


def get_dref(dref_name: str):
     dref = XPUDP.pyXPUDPServer.getData(dref_name)
     if dref == 0.0: # returns null when the value is asked for the first time
          time.sleep(1.0)
          dref = XPUDP.pyXPUDPServer.getData(dref_name)
     return dref


def wait_until_altitude_reached(expected_altitude, reset_time=False):
     '''
     Checks if altitude is reached. If not waits 0.5 seconds and check again.
     '''
     #altitude_not_reached = True
     #while altitude_not_reached:
     #     current_altitude = get_dreaf(DREF_INDICATOR_ALTI)
     #     altitude_delta = expected_altitude - current_altitude
     #     if abs(altitude_delta) < 50.0:
     #          altitude_not_reached = False 
     #     if reset_time:
     #          rst_msn_time()
     #     time.sleep(0.5)
     pass



def xp_config_enviroment():
     '''
     config weather etc.
     '''
     print('-------TODO---------')


def main():
     config_logger()
     init_xp_remote()

     xp_config_enviroment()

     #TODO reset fuel
     # climb and sink
     #fly_parable()
     
     #reset time
     rst_msn_time()          

     # banks
     #fly_banks()


#TODO server beim beenden des skripte runterfahren
# atexit.register(close_xp_remote)
if __name__ == "__main__":
     main()

