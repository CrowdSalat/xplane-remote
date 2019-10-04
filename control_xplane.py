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
     logger.debug('Start Server.')
     #XPUDP.pyXPUDPServer.initialiseUDP(('127.0.0.1',49008), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
     XPUDP.pyXPUDPServer.initialiseUDPXMLConfig('UDPSettings.xml')
     XPUDP.pyXPUDPServer.start() 
     logger.debug('Server started.')

def close_xp_remote():
     logger.debug('Shutdown Server.')
     XPUDP.pyXPUDPServer.quit()
     logger.debug('Server shutdown.')

def config_logger():
     logger.setLevel(logging.DEBUG)
     
     formatter = logging.Formatter('%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')
     
     ch = logging.StreamHandler()
     ch.setFormatter(formatter)

     script_path = os.path.dirname(sys.argv[0])
     fh = logging.FileHandler(os.path.join(script_path,'control_xplane.log'), encoding='utf-8')
     fh.setFormatter(formatter)

     logger.addHandler(ch)
     logger.addHandler(fh)

### MODES
def activate_mode_ap():
     set_dref(DREF_AP_ACTIVATE, 2.0)


def activate_mode_vs(activate=True):
     activate_mode(16.0, 5, activate)

def activate_mode_heading(activate=True):
     activate_mode(2.0, 2, activate)

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


### VALUES GET/ SET 
def rst_msn_time():
     set_dref(DREF_MISSN_TIME, 0.0)

def set_planned_climbrate(fpm: float):
     set_dref(DREF_AP_SET_VV_IN_FPM2,fpm)

def set_planned_altitude(target_altitude: float):
     set_dref(DREF_AP_SET_ALTI_IN_FEET,target_altitude)

def get_current_altitude():
     return get_dref(DREF_INDICATOR_ALTI)

def get_current_heading():
     return get_dref(DREF_INDICATOR_HEADING)


### DREF SET/GET
def set_dref(dref_name, target_value, index= 0):
     XPUDP.pyXPUDPServer.sendXPDref(dref_name,index,target_value)

def get_dref(dref_name: str):
     dref = XPUDP.pyXPUDPServer.getData(dref_name)
     if dref == 0.0: # returns null when the value is asked for the first time
          time.sleep(1.0)
          dref = XPUDP.pyXPUDPServer.getData(dref_name)
     return dref


### CHECK STATE

def wait_until_x_reached(function_to_load_actual_value, expected_value,tolerance,reset_time):
     function_to_load_actual_value()     
     value_not_reached = True
     while value_not_reached:
          current_value = function_to_load_actual_value()
          delta_value = expected_value - current_value
          if abs(delta_value) < tolerance:
               value_not_reached = False 
          if reset_time:
               rst_msn_time()
          time.sleep(1)

def wait_until_heading_reached(expected_heading, reset_time=False):
     wait_until_x_reached(get_current_heading, expected_heading, 2.0, reset_time)
     

def wait_until_altitude_reached(expected_altitude, reset_time=False):
     wait_until_x_reached(get_current_altitude, expected_altitude, 50.0,reset_time)

### MANEUVER


def set_bank_angle(level: int = 0):
     # 0=auto 1-6 for 5-30 bank degree in hdg mode
     set_dref(DREF_AP_SET_HEADING_LEVEL, 6.0) 

def set_heading_delta(delta: float):
     current_heading = get_current_heading()
     target_heading = (current_heading + delta) % 360.0
     set_heading(target_heading)
     return target_heading

def set_heading(heading: float):
     set_dref(DREF_AP_SET_HEADING_IN_DEGREE, heading)


def climb_to(altitude_target:float, fpm:float):
     cur_alti = get_current_altitude()
     delta = altitude_target - cur_alti

     fpm = abs(fpm)
     if delta < 0:
          fpm *= -1

     set_planned_altitude(altitude_target)
     activate_mode_vs()
     set_planned_climbrate(fpm)

def climb(altitude_delta:float, fpm:float):
     current_altitude = get_current_altitude()
     altitude_target = current_altitude + altitude_delta
     climb_to(altitude_target, fpm)
     return altitude_target


def fly_parable():
     start_alt = 1000.0
     altitude_delta = 200.0
     fpm = 500.0

     climb_to(start_alt, fpm)
     wait_until_altitude_reached(start_alt, reset_time=True)

     target_altitude = climb(altitude_delta, fpm)
     wait_until_altitude_reached(target_altitude)
     rst_msn_time()

     climb(-altitude_delta, -fpm)
     wait_until_altitude_reached(target_altitude)
     rst_msn_time()

def fly_banks(heading_delta = 15.0, bank_mode = 6):
     '''
     bank mode 1 - 6
     '''
     activate_mode_heading()
     set_bank_angle(bank_mode)
     target_heading = set_heading_delta(heading_delta)
     wait_until_heading_reached(target_heading)
     rst_msn_time()

def climb_wait_until_reached_and_reset_time(alt: float, fpm: float):
     target_alti = climb(alt, fpm)
     wait_until_altitude_reached(target_alti)
     rst_msn_time()

def first_trainingsset():

     # fixture
     start_alt = 1000
     climb_to(start_alt, 200)
     wait_until_altitude_reached(start_alt,reset_time=True)     

     #parable
     fpms = [200.0, 300.0, 400.0, 500.0]
     climbs = (-100, 150)


     for fpm in fpms:
          for climb in climbs:
               logger.info('Climb to {} ft with {} fpm.'.format(climb,fpm))
               climb_wait_until_reached_and_reset_time(climb, fpm)

     # banks
     bank_modes = {1,2,3,4,5,6}
     for bank in bank_modes:
          logger.info('Turn in Mode {}.'.format(bank))
          fly_banks(bank_mode=bank)



if __name__ == "__main__":
     pass
