#!/bin/bash

#GENERAL INSTRUCTIONS TO RUN THE SCRIPT
#Before running the script:
# chmod +x multicast_config-sh
#To run the script
#./multicast_config.sh

#If remote access uses not wifi network the sender IP address of mcast4.py must be added here!
#sudo ip route add <MY_IP>/32 dev wlan0
sudo ip route add 224.0.0.0/24 dev wlan0
#sudo ip -6 route add ff15:7079:7468:6f6e:6465:6d6f:6d63:6173 dev wlan0 table local
sudo sysctl -w net.ipv4.ip_forward=1
#sudo sysctl -w net.ipv6.conf.all.forwarding=1
