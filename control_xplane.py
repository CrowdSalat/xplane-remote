import pyxpudpserver as XPUDP
import logging
import os
import socket
import struct
import sys
import time
import itertools

logger = logging.getLogger('xplane-remote')

# DREF API Names 
DREF_OVERRIDE = 'sim/operation/override/override_planepath'
DREF_X = 'sim/flightmodel/position/local_x'                        # double	y	meters	The location of the plane in OpenGL coordinates                             
DREF_Y = 'sim/flightmodel/position/local_y'                        # double	y	meters	The location of the plane in OpenGL coordinates         
DREF_Z = 'sim/flightmodel/position/local_z'                        # double	y	meters	The location of the plane in OpenGL coordinates
DREF_MISSN_TIME = 'sim/time/total_flight_time_sec'                 # float	y	seconds	Total time since the flight got reset by something
DREF_INDICATOR_ALTI = 'sim/cockpit2/gauges/indicators/altitude_ft_pilot' #float	n	feet	Indicated height, MSL, in feet, primary system, based on pilots barometric pressure input.
DREF_INDICATOR_HEADING = 'sim/cockpit2/gauges/indicators/compass_heading_deg_mag'	     #float	n	degrees_magnetic	Indicated heading of the wet compass, in degrees.

DREF_THROTTLE = 'sim/cockpit2/engine/actuators/throttle_ratio_all'

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

def set_throttle(throttle :float):
     return set_dref(DREF_THROTTLE, throttle)

def get_current_altitude():
     return get_dref(DREF_INDICATOR_ALTI)

def get_planned_altitude():
     return get_dref(DREF_AP_SET_ALTI_IN_FEET)

def get_planned_climbrate():
     return get_dref(DREF_AP_SET_VV_IN_FPM2)

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
def reset_planned_altitude(target_altitude):
     planned_altitude = get_planned_altitude()
     if abs(planned_altitude - target_altitude) > 20.0:
          set_planned_altitude(target_altitude)

def correct_climb_direction(current_altitude, target_altitude):
     climbrate = get_planned_climbrate()
     false_direction = 0 > (target_altitude - current_altitude ) * climbrate
     if false_direction:
          set_planned_climbrate(climbrate * -1)

def wait_until_heading_reached(expected_heading):
     wait_until_reached(-1 , expected_heading)

def wait_until_altitude_reached(expected_altitude):
     wait_until_reached(expected_altitude, -1)

def wait_until_reached(target_altitude: float, target_banks: float):
     check_altitude = target_altitude >= 0
     dif_altitude = 0
     check_heading = target_banks >= 0
     dif_heading = 0
     while True:
          if check_altitude:
               cur_alt = get_current_altitude()
               dif_altitude = abs(target_altitude - cur_alt)
               reset_planned_altitude(target_altitude)
               correct_climb_direction(cur_alt, target_altitude)
          if check_heading:
               cur_head = get_current_heading ()
               dif_heading = abs(target_banks - cur_head)
          
          if( dif_altitude < 20.0 and 
          dif_heading < 2.0):
               break
          time.sleep(1.0)

### MANEUVER

def set_bank_angle(level: float = 0.0):
     # 0=auto 1-6 for 5-30 bank degree in hdg mode
     set_dref(DREF_AP_SET_HEADING_LEVEL, level) 

def set_heading_delta(delta: float):
     current_heading = get_current_heading()
     target_heading = (current_heading + delta) % 360.0
     set_heading(target_heading)
     return target_heading

def set_heading(heading: float):
     set_dref(DREF_AP_SET_HEADING_IN_DEGREE, heading)


def climb_to(altitude_target:float, fpm:float):
     if altitude_target <= 0:
          return
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
     if altitude_delta == 0:
          return current_altitude
     altitude_target = current_altitude + altitude_delta
     climb_to(altitude_target, fpm)
     return altitude_target

def fly_banks(heading_delta = 90.0, bank_mode = 6.0):
     '''
     bank mode 1 - 6
     '''
     activate_mode_heading()
     set_bank_angle(bank_mode)
     # let the direction settle
     set_heading_delta(heading_delta/10)
     time.sleep(2.0)
     return set_heading_delta(heading_delta)

### maneuver definition and execution

def define_flight_maneuver(start_altitude, climb, climb_rate, heading_change, bank_angle):
     ''' return dict with the given parameters'''
     ret = {
          "start_altitude": start_altitude,
          "climb": climb,
          "climb_rate": climb_rate,
          "heading_change": heading_change,
          "bank_angle": bank_angle
          }
     return ret

def define_flight_maneuvers(start_altitudes, climbs, climb_rates, heading_changes, bank_angles, sort=False):
     '''returns list with all one dict for each permutation of the parameters'''
     permutations = list(itertools.product(start_altitudes, climbs, climb_rates,
          heading_changes, bank_angles))
     manuveuvers = []
     for permutation in permutations:
          manuveuver = define_flight_maneuver(*permutation)
          manuveuvers.append(manuveuver)
     if sort:
          return sort_maneuvers(manuveuvers)
     else:
          return manuveuvers

def sort_maneuvers(manuveuvers):
     return sorted(manuveuvers, key=lambda k: (k['start_altitude'], k['climb_rate'],k['bank_angle'])) 
 
     
def fly(maneuvers, settle_time=6.0):
     '''
     maneuvers -- which are generated with define_flight_maneuvers
     '''
     for maneuver in maneuvers:
          logger.info(maneuver)
          start_altitude_param = maneuver["start_altitude"]
          climb_rate_param = maneuver["climb_rate"]
          climb_param = maneuver["climb"]
          heading_change_param = maneuver["heading_change"]
          bank_level_param =  maneuver["bank_angle"]
          activate_mode_ap()
          # reach start altitude and reset time
          if start_altitude_param > 0:
               climb_to(start_altitude_param, climb_rate_param)
               wait_until_altitude_reached(start_altitude_param)
               rst_msn_time()

          # do maneuver
          target_altitude = climb(climb_param, climb_rate_param)
          target_banks = fly_banks(heading_change_param, bank_level_param)
          wait_until_reached(target_altitude, target_banks)
          time.sleep(settle_time)
          rst_msn_time()

if __name__ == "__main__":
     pass
