#!/usr/bin/env python
# #################################################
## ACCESS TO IN-VEIHICLE SENSORS/ATUATORS AND GPS
#################################################
import time
from in_vehicle_network.car_motor_functions import init_vehicle_info, open_vehicle, close_vehicle, turn_vehicle_off, turn_vehicle_on, new_movement, new_direction, new_speed, stop_vehicle
from in_vehicle_network.location_functions import position_update
import in_vehicle_network.obd2 as obd2
import application.app_config as app_conf
import application.app_config_obu as app_obu_conf


#-----------------------------------------------------------------------------------------
# Thread - update location based on last known position, movement direction and heading. 
#         Note: No speed information and vehicles measurements are included.
#         TIP: In case, you want to include them, use obd_2_interface for this purpose
#-----------------------------------------------------------------------------------------
def update_location(node_interface, start_flag, coordinates, visual):
	gps_time = 2

	node = node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: update_location - NODE: {}\n'.format(node),'\n')


	while True:
		time.sleep(gps_time)
		position_update(coordinates, node_interface, visual)
	return


#-----------------------------------------------------------------------------------------
# Car Finite State Machine
# 		initial state: 	closed  - Car is closed and GPIO/PWN are not initialise
#				input: 	car_command = 'e' (open car): next_state: opened
#		next_state:		opened 	- Car is open and GPIO/PWN are initialised
#				input: 	car_command = '1' (turn on):	next_state: ready
#						car_command = 'x' (disconnect): next_state: closed
# 		next_state:		ready	- Car is able to move 
#				input: 	car_command in ['f','b'] (move forward or backward) - next_state: moving
#                       car_command in ['l','r'] (turn left or right) - next_state: same state
#                       car_command in ['i','d'] (increase or decrease speed) - next_state: same state  
#                       car_command = 's' (stop) - next_state: stop
# 						car_command = '0' (turn off):	next_state: not_ready
# 						car_command = 'x' (disconnect): next_state: closed	
# 		next_state:		moving/stopped	- car is moving or stop
#				input: 	car_command in ['f','b', 'l','r',i','d','s','0','x'] similar to ready state
# 		next_state:		not_ready	- Car is turned off and not reasy to move
#				input: 	car_command = '1' (turn on):	next_state: ready
# 						car_command = 'x' (disconnect): next_state: closed	 				
#-----------------------------------------------------------------------------------------
#obd_2_interface:  speed, speed_var, direction, steering_wheel, heading,  vehicle_status)
#-----------------------------------------------------------------------------------------
# Thread - control the car movement - uses the FSM described before
#-----------------------------------------------------------------------------------------
def movement_control(obd_2_interface, start_flag, coordinates, movement_control_txd_queue):
	
	node = obd_2_interface['node_id']

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: movement_control - NODE: {}\n'.format(node),'\n')
	
	init_vehicle_info(obd_2_interface)

	while True:
		move_command=movement_control_txd_queue.get()
	
		if (obd_2_interface['vehicle_status'] == obd2.closed):
			if (move_command == 'e'):			
				pwm_tm_control, pwm_dm_control, obd_2_interface=open_vehicle(obd_2_interface)
				command = 'car_opened'
		elif (obd_2_interface['vehicle_status'] == obd2.opened):
			if (move_command == '1'):	
				obd_2_interface=turn_vehicle_on(obd_2_interface)
				command = 'car_on' 
			elif (move_command == 'x'):
				obd_2_interface=close_vehicle(obd_2_interface)
				commmand = 'car_closed'
		elif (obd_2_interface['vehicle_status'] == obd2.not_ready):
			if (move_command == 'x'):
				obd_2_interface=close_vehicle(obd_2_interface)
				commmand = 'car_closed'
			elif (move_command == '1'):	
				obd_2_interface=turn_vehicle_on(obd_2_interface)
				commmand = 'car_on'
		elif ((obd_2_interface['vehicle_status'] == obd2.ready) or
			(obd_2_interface['vehicle_status'] == obd2.moving) or
			(obd_2_interface['vehicle_status'] == obd2.stoped)):
			if (move_command in ['f','b']):
				obd_2_interface=new_movement(move_command,obd_2_interface)
				commmand = 'car_moving'
			elif (move_command in ['l','r','f','b']): #forward e backward para seguir com o movimento...
				obd_2_interface=new_direction(move_command,obd_2_interface)
				commmand = 'car_moving'
			elif (move_command in ['i','d','i2','d2']):	
				obd_2_interface= new_speed(move_command, obd_2_interface, pwm_tm_control)
				commmand = 'car_change_speed'
			elif (move_command == 's'):
				obd_2_interface=stop_vehicle(obd_2_interface)
				commmand = 'car_stop'
			elif (move_command == '0'):
				obd_2_interface=turn_vehicle_off(obd_2_interface)
				commmand = 'car_off'
			elif (move_command == 'x'):
				obd_2_interface=close_vehicle(obd_2_interface)
				commmand = 'car_closed'
			else:
				print ('\n\nobd_2_interface', obd_2_interface, 'movement', move_command)
				print ('ERROR: movement control -> invalid status\n\n')

		#time.sleep(app_obu_conf.movement_update_time)

	return
