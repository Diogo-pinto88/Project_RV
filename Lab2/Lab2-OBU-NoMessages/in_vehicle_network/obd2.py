#!/usr/bin/env python
# #################################################
## ACCESS TO IN-VEIHICLE SENSORS/ATUATORS AND GPS
#################################################


#-----------------------------------------------------------------------------------------
# OBD2 interface parameters
#-----------------------------------------------------------------------------------------


#obd_2_interface: type, speed, speed_var, direction, steering_wheel, heading,  vehicle_status)

#direction
forward = "f"		# Forward direction
backward = "b"		# Backward direction

#steering_wheel
left = "l"			# Left
right = "r"			# Right
front = "-"			# Front or back

#user input: speed, heading

#vehicle_status
not_ready = 0       # Car is closed and turned off (gpio standby not active)
closed = 1			# Car is closed and GPIO/PWN are not initialised
opened = 2			# Car is open and GPIO/PWN are initialised
ready  = 3			# Car is ready to move forward, backward, turn left or right or stop and enable is turned on (gpio standby is active)
moving = 4          # Car is moving
stoped = 5          # Car is stoped

#speed_var
no_speed_var = 0
speed_inc = 10			# TIP: you can configure these limits you you want to change the step of speed variance
speed_dec = -10


#heading change due to turn movements
next_heading ={'l':{'N':'O','S':'E','E':'N','O':'S'},'r':{'N':'E','S':'O','E':'S','O':'N'}}

