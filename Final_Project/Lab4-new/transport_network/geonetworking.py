#!/usr/bin/env python
# #################################################
##SENDING/RECEIVING GEONETWORK - here we add the geonetworking information - ROI and neighbour management.
# You may need to add a common data structure with the neighbous table.
#################################################
import sys, os, time, threading
from transport_network.geo import *
from gps_info.gps_reader import position_read
import application.app_config as app_conf

sys.path.append(os.path.abspath(".."))
import ITS_options as its_conf


loc_table=dict()
pkt_beacon=dict()

lock_loc_table = threading.Lock()

#------------------------------------------------------------------------------------------------
# Thread - geonetwork_txd - message transmission in geocast mode. 
#		Note: current version is just a place holder. Future versions must include support for:
# 			1) geocast communication - messsages are trasmitted only it the node has, at least, one neigbour
#			2) unicast communication - location-based routing and a location service
#------------------------------------------------------------------------------------------------
def geonetwork_txd(node_interface, start_flag, geonetwork_txd_queue, multicast_txd_queue):

	node_id = node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: geonetwork_txd - NODE: {}\n'.format(node_id),'\n')

	while True :
		msg_rxd=geonetwork_txd_queue.get()
		if (app_conf.debug_geo_net):
			print('STATUS: Message received from getnetwork queue  - THREAD: geonetwork_txd - NODE: {}'.format(node_id),' - MSG: {}'.format(msg_rxd),'\n')
		if (its_conf.geonetwork_model):
			if loc_table:
				if (app_conf.debug_geo_net):
					print('STATUS: Message send to multicast queue - THREAD: geonetwork_txd - NODE: {}'.format(node_id),' - MSG: {}'.format(msg_rxd),'\n')
				multicast_txd_queue.put(msg_rxd)
			else:
				if (app_conf.debug_geo_net):
					print('STATUS: Message discarded (empty loc_table) - THREAD: geonetwork_txd - NODE: {}'.format(node_interface["node_id"]),' - MSG: {}'.format(msg_rxd),'\n')
		else:
			if (app_conf.debug_geo_net):
				print('STATUS: Message send to multicast queue - THREAD: geonetwork_txd - NODE: {}'.format(node_id),' - MSG: {}'.format(msg_rxd),'\n')
			multicast_txd_queue.put(msg_rxd)
	return
#------------------------------------------------------------------------------------------------
# Thread - geonetwork_rxd - message transmission in geocast mode. 
#	Note: current version is just a place holder. Future versions must include support for:
#		1) geocast communication - including region-of-interest (roi) processing
#		2) unicast communication - location-based routing and a location service
#------------------------------------------------------------------------------------------------
def geonetwork_rxd(node_interface, start_flag, multicast_rxd_queue, geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue, geonetwork_rxd_spat_queue, geonetwork_rxd_ivim_queue,):

	global loc_table

	node_id = node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: geonetwork_rxd - NODE: {}'.format(node_interface["node_id"]),'\n')

	while True:
		msg_rxd=multicast_rxd_queue.get()
		if (app_conf.debug_geo_net):
			print('STATUS: Message received from multicast queue - THREAD: geonetwork_rxd - NODE: {}'.format(node_id),' - MSG: {}'.format(msg_rxd),'\n')
		if (msg_rxd['msg_type']=='CA'):
			geonetwork_rxd_ca_queue.put(msg_rxd)
		elif (msg_rxd['msg_type']=='DEN'):
			geonetwork_rxd_den_queue.put(msg_rxd)
		elif (msg_rxd['msg_type']=='SPAT'):
			geonetwork_rxd_spat_queue.put(msg_rxd)
		elif (msg_rxd['msg_type']=='IVIM'):
			geonetwork_rxd_ivim_queue.put(msg_rxd)

	return

#------------------------------------------------------------------------------------------------
# Thread - beacon_rxd - periodical transmission of beacon packets
#------------------------------------------------------------------------------------------------
def beacon_txd(node_interface, start_flag, coordinates, multicast_txd_queue):
	TXD_BEACON_INTERVAL = 5
	global loc_table

	node_id = node_interface['node_id']
	node_type = node_interface['type']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: beacon_txd - NODE: {}\n'.format(node_id),'\n')

	while True :
		time.sleep(TXD_BEACON_INTERVAL)
		x,y,t=position_read(coordinates)
		update_node_info(node_id, x, y, t)
		beacon_pkt_txd=create_beacon(node_id, node_type, x, y, t)
		if (app_conf.debug_beacon):
			print('STATUS: Beacon send to multicast queue - THREAD: beacon_txd - NODE: {}'.format(node_id),' - MSG: {}'.format(beacon_pkt_txd),'\n')
		multicast_txd_queue.put(beacon_pkt_txd)
	return
#------------------------------------------------------------------------------------------------
# Thread -- beacon_rxd - reception of beacon packets and loc_table update
#		Note: - entry_validity defines the timeout value. The value used is very high to avoid removing entries for the table
#------------------------------------------------------------------------------------------------
def beacon_rxd(node_interface, start_flag, beacon_rxd_queue):
	ENTRY_VALIDITY = 2000
	global loc_table

	node_id = node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: beacon_rxd - NODE: {}'.format(node_id),'\n')

	while True :
		beacon_pkt_rxd=beacon_rxd_queue.get()
		if (app_conf.debug_beacon):
			print('STATUS: Beacon received from beacon queue - THREAD:  beacon_rxd - NODE: {}'.format(node_id),' - MSG: {}'.format(beacon_pkt_rxd),'\n')
		neighbour_node=update_loc_table_entry (node_id, loc_table, beacon_pkt_rxd, lock_loc_table, ENTRY_VALIDITY)
		if (app_conf.debug_beacon):
			print('STATUS: Loc_table_updated - THREAD:  beacon_rxd - NODE: {}'.format(node_id),' - MSG: {}'.format(loc_table),'\n')
	return

#------------------------------------------------------------------------------------------------
# Thread -- check_loc_table - verification of the loc_table status and remove unused entries
#		Note: - entry_validity defines the timeout value. The value used is very high to avoid removing entries for the table
#------------------------------------------------------------------------------------------------
def check_loc_table(node_interface, start_flag):
	global loc_table

	node_id = node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: check_loc_table - NODE: {}'.format(node_id),'\n')

	while True :
		time.sleep (1)
		delete_loc_table_entry(loc_table, node_id, lock_loc_table)
		if (app_conf.debug_beacon):
			print('STATUS: Loc_table_updated - THREAD:  check_loc_table - NODE: {}'.format(node_id),' - MSG: {}'.format(loc_table),'\n')
	return
