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
import application.app_config_au as app_au_conf


#-----------------------------------------------------------------------------------------
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
#-----------------------------------------------------------------------------------------
def au_application_txd(au_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
            print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(au_interface["node_id"]),'\n')



#-----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def au_application_rxd(au_interface, start_flag, services_rxd_queue, my_system_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(au_interface["node_id"]),'\n')
    
	while True :
          msg_rxd=services_rxd_queue.get()
          print ('application_au_rxd: ', msg_rxd)
          if (msg_rxd['msg_type']=="CA"):
               if (app_conf.debug_app_ca):
                    print ('au_application - ca messsage received ',msg_rxd)
               if (msg_rxd['node'] != au_interface["node_id"]):
                    if (msg_rxd['node_type'] == map.rsu_node):
                         if (app_conf.debug_app):
                           print ('au_application - external CA message from RSU node ', msg_rxd['node'])
                    elif (msg_rxd['node_type'] == map.obu_node):
                         if (app_conf.debug_app):
                           print ('au_application - external CA message from OBU node ', msg_rxd['node'])
                    else:
                         if (app_conf.debug_app):
                           print ('au_application - external CA message from AU node ', msg_rxd['node'])
               else:
                    if (app_conf.debug_app):
                         print ('au_application - internal CA message from RSU node ', msg_rxd['node'])
          elif (msg_rxd['msg_type']=="SPAT"):
               if (app_conf.debug_app_spat):
                    print ('\n....>au_application - spat messsage received ',msg_rxd)
          elif (msg_rxd['msg_type']=="VIM"):
               if (app_conf.debug_app_spat):
                    print ('\n....> au_application - ivim messsage received ',msg_rxd)

#-----------------------------------------------------------------------------------------
# Thread: my_system - person business logic
# 
#-----------------------------------------------------------------------------------------
def au_system(au_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue):
	
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(au_interface["node_id"]),'\n')
    


