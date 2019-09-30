#import pyxpudpserver as XPUDP
#import logging
#import writeDataToXPlane as my
#
#
#logging.basicConfig()
#logging.getLogger().setLevel(logging.INFO)
#
#xpr = XPUDP.pyXPUDPServer
#
#xpr.initialiseUDP(('127.0.0.1',50000), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
#xpr.start()
#print(xpr.getData('sim/flightmodel/position/longitude'))
#print(xpr.getData('sim/flightmodel/position/lon_ref'))
#print(xpr.getData('sim/time/total_flight_time_sec'))
#print(xpr.getData('sim/time/total_flight_time_sec'))
#print(xpr.getData('sim/time/total_flight_time_sec'))
#
#
#
#xpr.sendXPDref('sim/operation/override/override_planepath', 1, value = 1.0) 
#xpr.sendXPDref('sim/flightmodel/position/local_x', -100, value = 0.5) 
#xpr.quit()

import pyxpudpserver as XPUDP
XPUDP.pyXPUDPServer.initialiseUDP(('127.0.0.1',49008), ('192.168.23.192',49000), 'DESKTOP-0S9NHT3')
# where ('127.0.0.1',49008) is the IP and port this class is listening on (configure in the Net connections in XPlane)
# and ('192.168.1.1',49000) is the IP and port of XPlane
# 'MYPC' is the name of the computer XPlane is running on
# You can also initialise from an XML configuration file:
#XPUDP.pyXPUDPServer.initialiseUDPXMLConfig('UDPSettings.xml')

XPUDP.pyXPUDPServer.start() # start the server which will run an infinite loop

while True: # infinite loop - for a real application plan for a 'proper' way to exit the programme and break this loop
    value = XPUDP.pyXPUDPServer.getData((17,3)) 	# read the value sent by XPlane for datagroup 17, position 4 (mag heading)
    transp_mode = XPUDP.pyXPUDPServer.getData("sim/cockpit2/radios/actuators/transponder_mode[0]") # gets the value of this dataref in XPlane
    time = XPUDP.pyXPUDPServer.getData("sim/time/total_flight_time_sec") 
    print(str(value) + ' ' + str(transp_mode) + ' ' + str(time) )
    inp = input('-1 ende: ')
    if inp == '-1':
        break
    elif inp == '1':
        pass
    else:
        XPUDP.pyXPUDPServer.getData(inp) 

XPUDP.pyXPUDPServer.sendXPCmd('sim/engines/engage_starters') # send command to XPlane to engage the engine starters
XPUDP.pyXPUDPServer.sendXPDref("sim/flightmodel/controls/flaprqst", 0, value = 0.5) # set the requested flap deployment to 0.5 - bear in mind the flap will then deploy and take some time to do so - monitor its actual position if needed

XPUDP.pyXPUDPServer.quit() # exit the server thread and close the sockets
