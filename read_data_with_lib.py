import pyxpudpserver as XPUDP
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

XPUDP.pyXPUDPServer.initialiseUDP(('127.0.0.1',50000), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
print(XPUDP.pyXPUDPServer.getData('sim/flightmodel/position/longitude'))
print(XPUDP.pyXPUDPServer.getData('sim/flightmodel/position/lon_ref'))


XPUDP.pyXPUDPServer.quit()