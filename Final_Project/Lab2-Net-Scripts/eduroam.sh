#!/bin/bash

# Prompt for eduroam username and password
echo "Enter your eduroam username (usually your email address):"
read -r eduroam_username

echo "Enter your eduroam password:"
read -sr eduroam_password
echo # New line for better readability

# Create a UUID for the connection
uuid=$(uuidgen)

# Create the eduroam connection using nmcli
echo "Creating eduroam connection profile..."
nmcli connection add type wifi \
  con-name eduroam \
  ifname wlan0 \
  ssid eduroam \
  wifi-sec.key-mgmt wpa-eap \
  802-1x.eap peap \
  802-1x.identity "$eduroam_username" \
  802-1x.password "$eduroam_password" \
  802-1x.phase2-auth mschapv2 \
  connection.autoconnect yes \
  connection.uuid "$uuid"

# Bring the connection up
echo "Attempting to connect to eduroam..."
nmcli connection up eduroam

# Check connection status
if nmcli -t -f ACTIVE,SSID dev wifi | grep -q "^yes:eduroam$"; then
    echo "Successfully connected to eduroam."
else
    echo "Failed to connect to eduroam. Please check your credentials and try again."
fi

