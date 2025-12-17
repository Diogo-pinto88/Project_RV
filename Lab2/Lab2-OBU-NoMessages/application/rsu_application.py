#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time, threading
from application.message_handler import *
import application.app_config as app_conf
import application.app_config_rsu as app_rsu_conf
from application.rsu_commands import *
import ITS_maps as maps


#-----------------------------------------------------------------------------------------
# Thread: rsu application transmission. In this example user triggers CA and DEN messages. 
#   to be completed, in case RSU sends messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#        ca_service_txd_queue to send CA messages
#        den_service_txd_queue to send DEN messages
#-----------------------------------------------------------------------------------------
def rsu_application_txd(rsu_interface, start_flag,  my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, spat_service_txd_queue, ivim_service_txd_queue):



     while not start_flag.isSet():
          time.sleep (1)
     if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     time.sleep(app_rsu_conf.warm_up_time)



#-----------------------------------------------------------------------------------------
# Thread: rsu application reception. In this example it does not send or receive messages
#   to be completed, in case RSU receives messages
#   use: services_rxd_queue to receive messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#-----------------------------------------------------------------------------------------
def rsu_application_rxd(rsu_interface, start_flag, services_rxd_queue, my_system_rxd_queue):
     while not start_flag.isSet():
           time.sleep(1)
     if app_conf.debug_sys:
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(rsu_interface["node_id"]), '\n')



#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def rsu_system(rsu_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue):
     start_timer = None

     while not start_flag.isSet():
         time.sleep(1)
     if app_conf.debug_sys:
         print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(rsu_interface["node_id"]), '\n')
     time.sleep(app_rsu_conf.warm_up_time)

     while True:
         if not my_system_rxd_queue.empty():
             command = my_system_rxd_queue.get()
             if app_conf.debug_sys:
                 print(f"Received command: {command}")

             if command == "p":
                 parking_allowed = check_parking_availability()
                 if parking_allowed:
                     start_timer = time.time()
                     print("Parking allowed.")
                 else:
                     print("Parking not allowed.")

             elif command == "o":
                    if start_timer is not None:
                         # end parking, calculate duration and amount to pay
                         time_parked = (time.time() - start_timer) / 60  # in minutes
                         amount = amount_to_pay(time_parked)  # Example duration
                         print("Parking ended.")
                         print(f"Parking duration: {time_parked:.2f} minutes.")
                         print(f"Amount to pay: ${amount:.2f}")
                         start_timer = None  # reset timer
                    else:
                         print("Error: Parking was not started.")

def check_parking_availability():
     # Placeholder logic for checking parking availability
     # Replace with actual conditions
     return True  # Example: Always allow parking

def amount_to_pay(time_parked):
     # Placeholder logic for calculating amount to pay
     # Replace with actual calculation based on duration
     rate_per_hour = 2.0  # Example rate
     amount = time_parked * rate_per_hour
     return amount


