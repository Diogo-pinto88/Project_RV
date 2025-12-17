i#!/bin/bash

# Define the wireless interface, e.g., wlan0
interface="wlan0"

# Reset the wireless interface to managed mode
echo "Resetting $interface to Managed mode..."
sudo ip link set "$interface" down
sudo iwconfig "$interface" mode managed
sudo ip link set "$interface" up

# Restart NetworkManager to re-enable regular network management
echo "Restarting NetworkManager..."
sudo systemctl restart NetworkManager

# Prompt for Wi-Fi SSID and password
echo "Enter your Wi-Fi network name (SSID):"
read -r wifi_ssid

echo "Enter your Wi-Fi password:"
#read -sr wifi_password
read -r wifi_password

# Connect to the Wi-Fi network using nmcli
echo "Attempting to connect to $wifi_ssid..."
sudo nmcli dev wifi connect "$wifi_ssid" password "$wifi_password"

# Check connection status
if nmcli -t -f ACTIVE,SSID dev wifi | grep -q "^sim:$wifi_ssid"; then
    echo "Successfully connected to $wifi_ssid"
else
    echo "Failed to connect to $wifi_ssid. Please check the SSID and password and try again."
fi
