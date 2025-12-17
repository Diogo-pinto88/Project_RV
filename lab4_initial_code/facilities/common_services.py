#!/usr/bin/env python
# #######################################################################################################
# SENDING/RECEIVING SERVICES - Here you add the common services - CAM messages and DEN messages generation.
# In this structure both messages are generated and received by the same thread. But, you may want to have independent threads
##########################################################################################################
import time
from facilities.services import *
import application.app_config as app_conf

#------------------------------------------------------------------------------------------------
# Thread - ca_service_txd - periodical transmission of CA messages.
#------------------------------------------------------------------------------------------------
def ca_service_txd(node_interface, start_flag, coordinates, ca_service_txd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: ca_service_txd - NODE: {}'.format(node_interface["node_id"]),'\n')

	ca_msg=dict()
	msg_id =0
	generation_time=ca_service_txd_queue.get()
	while True :
		ca_msg_txd = create_ca_message(node_interface, msg_id, coordinates)
		geonetwork_txd_queue.put(ca_msg_txd)
		msg_id=msg_id+1
		time.sleep(generation_time)
		if (ca_service_txd_queue.empty()==False):
			generation_time=ca_service_txd_queue.get()
	return

#------------------------------------------------------------------------------------------------
# Thread - ca_service_exd - reception of CA messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def ca_service_rxd(node_interface, start_flag, geonetwork_rxd_ca_queue, services_rxd_queue):


	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: ca_service_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True :
		ca_msg_rxd=geonetwork_rxd_ca_queue.get()
		services_rxd_queue.put(ca_msg_rxd)
	return

#------------------------------------------------------------------------------------------------
# Thread - den_service_txd -  transmission of DEN messages.
#			Note: for message repetition, you need to include the repetition mechanism.
#------------------------------------------------------------------------------------------------
def den_service_txd(node_interface, start_flag, coordinates, den_service_txd_queue, geonetwork_txd_queue):
	
	node = node_interface["node_id"]

	node_type = node_interface["type"]
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: den_service_txd - NODE: {}'.format(node),'\n')
	
	msg_id =0
	while True :
		event=den_service_txd_queue.get()
		den_msg_txd=create_den_message(node_interface, msg_id, coordinates, event)
		geonetwork_txd_queue.put(den_msg_txd)
		msg_id=msg_id+1
	return

#------------------------------------------------------------------------------------------------
# Thread - den_service_exd - reception of DEN messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def den_service_rxd(node_interface, start_flag, geonetwork_rxd_den_queue, services_rxd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: den_service_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True :
		den_msg_rxd=geonetwork_rxd_den_queue.get()
		services_rxd_queue.put(den_msg_rxd)
	return


#novas threads
#------------------------------------------------------------------------------------------------
# Thread 	- spat_service_txd -  transmission of SPaT messages.
#			Note: not implemented yet
#------------------------------------------------------------------------------------------------
def spat_service_txd(node_interface, start_flag, coordinates, spat_service_txd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: spat_service_txd - NODE: {}'.format(node_interface["node_id"]),'\n')

	msg_id =0
	while True :
		spat_info=spat_service_txd_queue.get()
		spat_msg_txd=create_spat_message(node_interface, msg_id, coordinates,spat_info)
		geonetwork_txd_queue.put(spat_msg_txd)
		msg_id=msg_id+1
	return

#------------------------------------------------------------------------------------------------
# Thread 	- den_service_rxd - reception of SPaT messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def spat_service_rxd(node_interface, start_flag, geonetwork_rxd_spat_queue, services_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: spat_service_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True :
		spat_msg_rxd=geonetwork_rxd_spat_queue.get()
		print ('received spat at spat services')
		services_rxd_queue.put(spat_msg_rxd)
	return

#------------------------------------------------------------------------------------------------
# Thread 	- map_service_txd -  transmission of MAP messages.
#			Note: not implemented yet
#------------------------------------------------------------------------------------------------
def map_service_txd(node_interface, start_flag, coordinates, map_service_txd_queue, geonetwork_txd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: map_service_txd - NODE: {}'.format(node_interface["node_id"]),'\n')

	msg_id =0
	while True :
		event=map_service_txd_queue.get()
	#	den_msg_txd=create_map_message(node, msg_id, coordinates, event)
	#	geonetwork_txd_queue.put(map_msg_txd)
		msg_id=msg_id+1
	return

#------------------------------------------------------------------------------------------------
# Thread - map_service_rxd - reception of MAP messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def map_service_rxd(node_interface, start_flag, geonetwork_rxd_map_queue, services_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: map_service_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True :
		map_msg_rxd=geonetwork_rxd_map_queue.get()
		services_rxd_queue.put(map_msg_rxd)
	return


#------------------------------------------------------------------------------------------------
# Thread - ivim_service_txd -  transmission of IVIM messages.
#			Note: not implemented yet.
#------------------------------------------------------------------------------------------------
def ivim_service_txd(node_interface, start_flag, coordinates, ivim_service_txd_queue, geonetwork_txd_queue):


	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: ivim_service_txd - NODE: {}'.format(node_interface["node_id"]),'\n')

	msg_id =0
	validity = 100
	while True :
		situation=ivim_service_txd_queue.get()
		ivim_msg_txd=create_ivim_message(node_interface, msg_id, coordinates, validity, situation)
		geonetwork_txd_queue.put(ivim_msg_txd)
		msg_id=msg_id+1
	return

#------------------------------------------------------------------------------------------------
# Thread - ivim_service_exd - reception of IVIM messages and transmission to the application_rxd 
#------------------------------------------------------------------------------------------------
def ivim_service_rxd(node_interface, start_flag, geonetwork_rxd_ivim_queue, services_rxd_queue):

	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: ivim_service_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True :
		ivim_msg_rxd=geonetwork_rxd_ivim_queue.get()
		print ('ivim_service_rxd ', ivim_msg_rxd)
		services_rxd_queue.put(ivim_msg_rxd)
	return



#fim das novas threads
