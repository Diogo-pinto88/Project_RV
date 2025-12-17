#!/bin/bash

#GENERAL INSTRUCTIONS TO RUN THE SCRIPT
#Before running the script:
# chmod +x multicast_config-sh
#To run the script
#./multicast_config.sh


#  MACOS version - configuration for Wifi (ad-hoc mode)
sudo route -nv add -net 224.0.0.0/24 -interface en0
#sudo route -nv add -inet6 ff15:7079:7468:6f6e:6465:6d6f:6d63:6173 -interface en0
sudo sysctl -w net.inet.ip.forwarding=1
