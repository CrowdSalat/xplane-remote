
import pyxpudpserver as XPUDP
import logging
import os
import sys
import numpy as np
import matplotlib.pyplot as plt


logger = logging.getLogger('xplane_monitor')

# moments and derivitives
## X
DREF_ROLL_DEGREE        = 'sim/flightmodel/position/phi' #float	y	degrees	The roll of the aircraft in degrees - OpenGL coordinates
DREF_ROLL_DEGREE_RATE   = 'sim/flightmodel/position/P'	#float	y	deg/sec	The roll rotation rates (relative to the flight)
## Y
DREF_PITCH_DEGREE       = 'sim/flightmodel/position/theta'	#float	y	degrees	The pitch relative to the plane normal to the Y axis in degrees - OpenGL coordinates
DREF_PITCH_DEGREE_RATE  ='sim/flightmodel/position/Q'	#float	y	deg/sec	The pitch rotation rates (relative to the flight)
## Z
DREF_YAW_DEGREE         =   'sim/flightmodel/position/psi' #float	y	degrees	The true heading of the aircraft in degrees from the Z axis - OpenGL coordinates
DREF_YAW_DEGREE_RATE    ='sim/flightmodel/position/R'	#float	y	deg/sec	The yaw rotation rates (relative to the flight)

# forces and derivitives
## Z
#DREF_ALTITUDE           = 'sim/cockpit2/gauges/indicators/altitude_ft_pilot' #float	n	feet	Indicated height, MSL, in feet, primary system, based on pilots barometric pressure input.
DREF_ALTITUDE           = 'sim/flightmodel/position/elevation'	#double	n	meters	The elevation above MSL of the aircraft
#DREF_VERTICAL_VELOCITY  = 'sim/cockpit2/gauges/indicators/vvi_fpm_pilot'	#float	n	feet/minute	Indicated vertical speed in feet per minute, pilot system.
DREF_VERTICAL_VELOCITY = 'sim/flightmodel/position/vh_ind_fpm'	#float	y	fpm	VVI (vertical velocity in feet per second)
## X 
DREF_KTAS = 'sim/flightmodel/position/indicated_airspeed'	#float	y	kias	Air speed indicated - this takes into account air density and wind direction
DREF_KIAS = 'sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot'	#float	n	knots	True airspeed in knots, for pilot pitot/static, calculated by ADC, requires pitot, static, oat sensor and ADC all to work correctly to give correct value
DREF_engine_rpm = 'sim/cockpit2/engine/indicators/engine_speed_rpm[0]'	#float[8]	n	revolutions/minute	
##Y
## derived from ktas/tan(rollwinkel)

DREFS = []
DREFS.append(DREF_ROLL_DEGREE)
DREFS.append(DREF_ROLL_DEGREE_RATE)
DREFS.append(DREF_PITCH_DEGREE)
DREFS.append(DREF_PITCH_DEGREE_RATE)
DREFS.append(DREF_YAW_DEGREE)
DREFS.append(DREF_YAW_DEGREE_RATE)
DREFS.append(DREF_ALTITUDE)
DREFS.append(DREF_VERTICAL_VELOCITY)
DREFS.append(DREF_KTAS)
DREFS.append(DREF_KIAS)
DREFS.append(DREF_engine_rpm)




def config_logger():
     logger.setLevel(logging.DEBUG)
     
     formatter = logging.Formatter('%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')
     
     ch = logging.StreamHandler()
     ch.setFormatter(formatter)

     script_path = os.path.dirname(sys.argv[0])
     fh = logging.FileHandler(os.path.join(script_path,'monitor.log'), encoding='utf-8')
     fh.setFormatter(formatter)

     logger.addHandler(ch)
     logger.addHandler(fh)

def init_xp_remote():
     logger.info('Start Server.')
     XPUDP.pyXPUDPServer.initialiseUDP(('127.0.0.1',49008), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
     XPUDP.pyXPUDPServer.start() 
     logger.info('Server started.')

def close_xp_remote():
     logger.info('Shutdown Server.')
     XPUDP.pyXPUDPServer.quit()
     logger.info('Server shutdown.')

def draw():
    np.random.seed(19680801)

    mu, sigma = 100, 15
    x = mu + sigma * np.random.randn(10000)

    # the histogram of the data
    n, bins, patches = plt.hist(x, 50, density=True, facecolor='g', alpha=0.75)


    plt.xlabel('Smarts')
    plt.ylabel('Probability')
    plt.title('Histogram of IQ')
    plt.text(60, .025, r'$\mu=100,\ \sigma=15$')
    plt.xlim(40, 160)
    plt.ylim(0, 0.03)
    plt.grid(True)
    plt.show()

def main():
    init_xp_remote()

    for dref in DREFS:
        ref = XPUDP.pyXPUDPServer.getData(dref)
        draw()

    close_xp_remote()



if __name__ == "__main__":
    draw()
    #main()