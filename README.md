# control xplane python  

## Overview 
Controls the G1000 Autopilot in the flight simulator X-Plane 11 via the DataRef API. For the handling of the sockets and the DataRef protocol the python module [pyXPUDPServer](https://github.com/leleopard/pyXPUDPServer) is used.

## Firewall config

Note that you need to open some UDP ports in your firewall if you run the script on another machine as the script.

For the windows computer, which is running X-Plane, you need to open at least the incoming port 49000. If not configured otherwise it is the default incoming port of X-Plane. [Manual for Windows](https://www.thewindowsclub.com/block-open-port-windows-8-firewall).

On the the client machine, which runs the script, you need to open all udp ports. The library *pyXPUDPServer* opens multiple sockets on different ports. I recommend to delete this firewall rule as soon as you are finished running the script.

On a linux machine you can create a firewall rule (temporarly) and delete it with:

``` shell
# creates firewall rule (hold only until next restart)
sudo iptables -I INPUT -p udp -j ACCEPT

#deltes the firewall rule
sudo iptables -D INPUT -p udp -j ACCEPT
```

**The creation will only hold until the next restart.**

## libraries

``` shell
pip3 install pyxpudpserver
```
