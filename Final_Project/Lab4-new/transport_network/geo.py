#!/usr/bin/env python
# #################################################
## FUNCTIONS USED BY GEONETWORK LAYER
#################################################
import time
from Queue import Empty

#------------------------------------------------------------------------------------------------
# create_beacon - a beacon is a keep-alive packet used to maintain up-to-date information of neighnour nodes
#------------------------------------------------------------------------------------------------
def create_beacon(node, type,  x, y, t):
	beacon_pkt = {'msg_type':'BEACON', 'node':str(node), 'node_type': type, 'pos_x':x, 'pos_y':y, 'time':t}
	return beacon_pkt

#------------------------------------------------------------------------------------------------
# update_node_info - node information to be included on an beacon
#------------------------------------------------------------------------------------------------
def update_node_info(node, x, y, t):
	node_info = {'node': node, 'pos_x': x, 'pos_y':y, 'time': t}
	return node_info

#------------------------------------------------------------------------------------------------
# update_loc_table_entry - node's neighbourhood is maintained on a table - the loc_table. 
# 					This table ia update upon reception of a beacon from a neighbour node
#------------------------------------------------------------------------------------------------
def update_loc_table_entry(node,loc_table, beacon, lock, validity):
	neighbour_node=beacon['node']
	if (neighbour_node==node):
		return -1
	lock.acquire()
	timer = time.time()+validity
	loc_table.update({beacon['node']:{'node': beacon['node'], 'pos_x':beacon['pos_x'],'pos_y':beacon['pos_y'],'timeout':timer}})
	print ('loc_table', loc_table)
	lock.release()
	return node

#------------------------------------------------------------------------------------------------
# delete_loc_table_entry - loc_table entries are removed after a timeout period without receiving a beacon 
# 				from the correspodent node. This function checks for invalid entries.
#------------------------------------------------------------------------------------------------
def delete_loc_table_entry(loc_table, node, lock):
	if loc_table is not Empty:
		for neighbour in list(loc_table):
			if (node!=neighbour) and (time.time()>loc_table[neighbour]['timeout']):
				lock.acquire()
				del (loc_table[neighbour])
				lock.release()
	return

#------------------------------------------------------------------------------------------------
# to be done, if needed
#------------------------------------------------------------------------------------------------
def check_roi(node_info, pos, roi):
	in_roi=True
	return in_roi

#------------------------------------------------------------------------------------------------
# to be done, if needed
#------------------------------------------------------------------------------------------------
def find_next_hop(node_info, loc_table, dest_node):
	next_hop=0
	return next_hop
