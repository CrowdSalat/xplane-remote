
import pyxpudpserver as XPUDP
import logging
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import time


logger = logging.getLogger('xplane_monitor')

# moments and derivitives
# X
# float	y	degrees	The roll of the aircraft in degrees - OpenGL coordinates
DREF_ROLL_DEGREE = 'sim/flightmodel/position/phi'
# float	y	deg/sec	The roll rotation rates (relative to the flight)
DREF_ROLL_DEGREE_RATE = 'sim/flightmodel/position/P'
# Y
# float	y	degrees	The pitch relative to the plane normal to the Y axis in degrees - OpenGL coordinates
DREF_PITCH_DEGREE = 'sim/flightmodel/position/theta'
# float	y	deg/sec	The pitch rotation rates (relative to the flight)
DREF_PITCH_DEGREE_RATE = 'sim/flightmodel/position/Q'
# Z
# float	y	degrees	The true heading of the aircraft in degrees from the Z axis - OpenGL coordinates
DREF_YAW_DEGREE = 'sim/flightmodel/position/psi'
# float	y	deg/sec	The yaw rotation rates (relative to the flight)
DREF_YAW_DEGREE_RATE = 'sim/flightmodel/position/R'

# forces and derivitives
# Z
# float	n	feet	Indicated height, MSL, in feet, primary system, based on pilots barometric pressure input.
DREF_GAUGE_ALTITUDE = 'sim/cockpit2/gauges/indicators/altitude_ft_pilot'
# double	n	meters	The elevation above MSL of the aircraft
DREF_ALTITUDE = 'sim/flightmodel/position/elevation'
# float	n	feet/minute	Indicated vertical speed in feet per minute, pilot system.
DREF_GAUGE_VERTICAL_VELOCITY = 'sim/cockpit2/gauges/indicators/vvi_fpm_pilot'
# float	y	fpm	VVI (vertical velocity in feet per second)
DREF_VERTICAL_VELOCITY = 'sim/flightmodel/position/vh_ind_fpm'
# X
# float	y	kias	Air speed indicated - this takes into account air density and wind direction
DREF_KTAS = 'sim/flightmodel/position/indicated_airspeed'
# float	n	knots	True airspeed in knots, for pilot pitot/static, calculated by ADC, requires pitot, static, oat sensor and ADC all to work correctly to give correct value
DREF_KIAS = 'sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot'
# float[8]	n	revolutions/minute
DREF_engine_rpm = 'sim/cockpit2/engine/indicators/engine_speed_rpm[0]'
# Y
# derived from ktas/tan(rollwinkel)

DREFS = {}
DREFS[DREF_ROLL_DEGREE] = 0.0
DREFS[DREF_ROLL_DEGREE_RATE] = 0.0
DREFS[DREF_PITCH_DEGREE] = 0.0
DREFS[DREF_PITCH_DEGREE_RATE] = 0.0
DREFS[DREF_YAW_DEGREE] = 0.0
DREFS[DREF_YAW_DEGREE_RATE] = 0.0
DREFS[DREF_ALTITUDE] = 0.0
DREFS[DREF_VERTICAL_VELOCITY] = 0.0
DREFS[DREF_KTAS] = 0.0
DREFS[DREF_KIAS] = 0.0
DREFS[DREF_engine_rpm] = 0.0
DREFS[DREF_GAUGE_VERTICAL_VELOCITY] = 0.0
DREFS[DREF_GAUGE_ALTITUDE] = 0.0


def config_logger():
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s-%(funcName)s - %(levelname)s - %(message)s')

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)

    script_path = os.path.dirname(sys.argv[0])
    fh = logging.FileHandler(os.path.join(
        script_path, 'monitor.log'), encoding='utf-8')
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)


def init_xp_remote():
    logger.info('Start Server.')
    XPUDP.pyXPUDPServer.initialiseUDP(
        ('127.0.0.1', 49008), ('192.168.23.192', 49000), 'DESKTOP-0S9NHT3')
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

     for dref_key in DREFS.keys():
          DREFS[dref_key] = XPUDP.pyXPUDPServer.getData(dref_key)
     time.sleep(1)
     
     for dref_key in DREFS.keys():
          print(dref_key)
          result = XPUDP.pyXPUDPServer.getData(dref_key)
          print(result)
          DREFS[dref_key] = result
     
     print(DREFS)
     close_xp_remote()


if __name__ == "__main__":
     main()
