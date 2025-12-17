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
from facilities.services import create_ivim_message
import ITS_maps as maps

status_update = threading.Condition()

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

     msg_counter = 0
     
     while True:
          #wait for notification of tls status alteration to tramsit a spat message
          with status_update:
              status_update.wait() 
          spat=spat_generation(rsu_interface)
          spat_service_txd_queue.put(spat)
          #roadwork information
          roadworks_info = {
              'msg_sub_type': 'road_works',
              'roadwork_information': {
                   'work_zone_type': 'road_repair', 
                   'work_zone_status': 'active'
              }
          }

          #Create IVIM message
          ivim_msg = create_ivim_message(rsu_interface, msg_counter, {'x': 0, 'y': 0, 't': 0}, 100, roadworks_info)
          
          # Send IVIM message
          ivim_service_txd_queue.put(ivim_msg)
          
          if (app_conf.debug_sys):
               print(f"RSU: Enviado SPAT + IVIM (Roadworks Warning ID {msg_counter})")

          msg_counter += 1
          


#-----------------------------------------------------------------------------------------
# Thread: rsu application reception. In this example it does not send ot receive messages
#   to be completed, in case RSU receives messages
#   use: services_rxd_queue to receive messages
#        my_system_rxd_queue to send commands/messages to rsu_system
#-----------------------------------------------------------------------------------------
def rsu_application_rxd(rsu_interface, start_flag, services_rxd_queue, my_system_rxd_queue):
     
     while not start_flag.isSet():
           time.sleep (1)
     if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     
     


#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def rsu_system(rsu_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue):
    
     while not start_flag.isSet():
         time.sleep (1)
     if (app_conf.debug_sys):
         print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(rsu_interface["node_id"]),'\n')
     time.sleep (app_rsu_conf.warm_up_time)

     #init rsu
     start_rsu(rsu_control_txd_queue)
     turn_on(rsu_control_txd_queue)
     
     #init intersection variables
     #tls_groups: dictionary containing all the tls of the intersection
     #num_tls: number of tls of the intersection
     #keys: IDs of the tls of the intersection
     tls_group = maps.map[rsu_interface["node_id"]]['tls_groups']
     num_tls = maps.map[rsu_interface["node_id"]]['num_tls']
     keys = list(tls_group.keys())

     #initial value used to guarantee the while execution
     data = 's'
     while (data != 'x'):
          # case 1: intersection with 1 tls - used to control a road with a single lane.
          if num_tls == 1:
               single_tls (tls_group, rsu_control_txd_queue)
          # case 2: intersection with 2 tls - used to control a road with two lanes.
          elif num_tls == 2: 
               key_s1 = keys[0]
               key_s2 = keys[1] 
               same_state = False
               #case 2.1 - tls controls two lanes of the same road, one in each direction. The 2 tls share the same status.
               #case 2.w - tls controls two lanes of the different roads. The 2 tls do not share the same status.
               if (tls_group[key_s1]['state']==tls_group[key_s2]['state']):
                    same_state = True     
               if (same_state):
                    single_lane_tls(tls_group, rsu_control_txd_queue)
               else:
                    multiple_lane_tls(tls_group, rsu_control_txd_queue)
          # case 2: intersection with 4 tls - used to control two roads with two lanes each.
          elif num_tls == 4:
               junction_tls (tls_group, rsu_control_txd_queue)
          # Notify the new tls status to trigger spat message transmission
          with status_update:
               status_update.notify()
          time.sleep(app_rsu_conf.tls_timing)
     #cancel RSU
     turn_off(rsu_control_txd_queue)
     exit_rsu(rsu_control_txd_queue)
     
