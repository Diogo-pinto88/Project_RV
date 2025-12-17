#Free resources: stop wpa_supplicant execution
echo "Free resources: stop wpa_supplicant execution"
sudo systemctl stop wpa_supplicant

#Free resources: stop NetworkManager
echo "Free resources: stop NetworkManager"
sudo systemctl stop NetworkManager
#!/bin/bash
#Turn off wirless network interface
"Turn off wirless network interface"
sudo ifconfig wlan0 down

#Ad-hoc mode configuration
echo "d-hoc mode configuration"
sudo iwconfig wlan0 mode ad-hoc
sudo iwconfig wlan0 essid "RV-3"
sudo iwconfig wlan0 channel 6

#Wireless network IP address configuration
echo "Wirelesss network IP address configuration"
sudo ifconfig wlan0 10.0.3.1  netmask 255.255.255.0

#Turn on wireless network interface
echo "Turn on wireless network interface"
sudo ifconfig wlan0 up

#Wireless interface check
echo "Wireless interface check"
iwconfig

