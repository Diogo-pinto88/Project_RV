#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time
import ITS_maps as map
from application.message_handler import *
from application.obu_commands import *
import application.app_config as app_conf
import application.app_config_obu as app_obu_conf


#-----------------------------------------------------------------------------------------
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
#-----------------------------------------------------------------------------------------
def obu_application_txd(obd_2_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
            print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(obd_2_interface["node_id"]),'\n')



#-----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def obu_application_rxd(obd_2_interface, start_flag, services_rxd_queue, my_system_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(obd_2_interface["node_id"]),'\n')
    
          
#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def obu_system(obd_2_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue):
    
    # Wait for start flag
    while not start_flag.isSet():
        time.sleep(1)

    if (app_conf.debug_sys):
        print('STATUS: Ready to start AUTONOMOUS SEQUENCE - NODE: {}'.format(obd_2_interface["node_id"]), '\n')

    # ============================================================
    # AUTONOMOUS MANOEUVRE SEQUENCE
    # ============================================================

    print("\n>>> Autonomous mode: Moving FORWARD for 2 meters...")
    open_car(movement_control_txd_queue)
    turn_on_car(movement_control_txd_queue)

    # Move forward (approximate timing to reach 2 m)
    car_move_forward(movement_control_txd_queue)
    time.sleep(2.0)   # Adjust based on real vehicle speed
    stop_car(movement_control_txd_queue)

    print(">>> Stopping for 5 seconds...")
    time.sleep(5)

    print(">>> Autonomous mode: Moving BACKWARD slowly for 2 meters...")
    car_move_slower(movement_control_txd_queue)  # enter “slow” mode
    car_move_backward(movement_control_txd_queue)
    time.sleep(2.0)   # Same duration for backward movement

    stop_car(movement_control_txd_queue)
    turn_off_car(movement_control_txd_queue)
    close_car(movement_control_txd_queue)

    print("\n>>> Autonomous manoeuvre complete! Switching to MANUAL mode.\n")

    # ============================================================
    # MANUAL MODE (unchanged)
    # ============================================================

    select_option_menu()
    data = '-'

    while data != 'x':
        data = input()

        if (data == 'e'):
            open_car(movement_control_txd_queue)
        elif (data == '1'):
            turn_on_car(movement_control_txd_queue)
        elif (data == '0'):
            turn_off_car(movement_control_txd_queue)
        elif (data == 'f'):
            car_move_forward(movement_control_txd_queue)
        elif (data == 'b'):
            car_move_backward(movement_control_txd_queue)
        elif (data == 'r'):
            car_turn_right(movement_control_txd_queue)
        elif (data == 'l'):
            car_turn_left(movement_control_txd_queue)
        elif (data == 'i'):
            car_move_faster(movement_control_txd_queue)
        elif (data == 'd'):
            car_move_slower(movement_control_txd_queue)
        elif (data == 's'):
            stop_car(movement_control_txd_queue)
        else:
            print('Invalid command')

    close_car(movement_control_txd_queue)
