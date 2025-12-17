#!/usr/bin/env python
# #################################################
##SENDING/RECEIVING MULTICAST - here you do not need to add anything. 
# Unless, we intend to emulate the physical medium.
# For this, you just need to drop incoming packets when the distance between the sender and the receiver 
# is higher than a threshold value
#################################################
import time
import socket
import struct, json
import math, random
import application.app_config as app_conf
import ITS_maps as map
import ITS_options as its_conf

# #####################################################################################################
# message fields definition
MSG_TYPE = 0

# Multicast IPv4 address  
# The values in the range [224.0.0.0 and 224.0.0.255] are reserved for routing, gateway discovery, group multicast reporting and other low level protocols
MYGROUP_4 = '224.0.0.0'

# Multicast receiver port
PORT=4260

# time-to-live (ttl) value of multicast packets that defines how many networks receive the packet. Packets are dropped when ttl=0. 
# Default value = 1
# Other possibilities for ttl value:
# 		0 - same host
# 		1 - same subnet
# 		32 - same site
# 		64 - same region
# 		128 - same continent
# 		255 - unrestricted.
MY_TTL = 1 

# Packet size
MSG_SIZE=1024

def multicast_txd(node_interface, start_flag, multicast_txd_queue):

	node=node_interface['node_id']
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: multicast_txd - NODE: {}'.format(node),'\n')

	#Translates host/port (not used here) into a sequence of 5 tupples (family, type, proto, canonname, sockaddr) 
	#Used o to obtain family information AF_INET
	addrinfo=socket.getaddrinfo(MYGROUP_4, None)[0]
	
	#Create an UDP socket 
	s=socket.socket(addrinfo[0], socket.SOCK_DGRAM)

	# Use ttl=1 (default value). When ttl=o packet is dropped.
	ttl_bin=struct.pack('@I', MY_TTL)

	# Select ttl value for IPv4 multicast
	# 		IPPROTO_IP - IPv4 protocol	
	#		MULTICAST_TTL - set ttl value
	s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
	
	msg = dict()
	while True:
		rxd_msg=multicast_txd_queue.get()
		data_to_send=s.sendto(json.dumps(rxd_msg).encode('utf-8'), (addrinfo[4][0], PORT))
		if (app_conf.debug_multicast):
			print('STATUS: Packet transmitted - THREAD: multicast_txd - NODE: {}'.format(node),' - MSG: {}'.format(data_to_send),'\n')
	return


def multicast_rxd(node_interface, start_flag, coordinates, multicast_rxd_queue, beacon_rxd_queue):

	node=node_interface['node_id']	
	while not start_flag.isSet():
		time.sleep (1)
	if (app_conf.debug_sys):
		print('STATUS: Ready to start - THREAD: multicast_rxd - NODE: {}'.format(node),'\n')

	#Create an UDP/IPv4 socket 
	r=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


	#Allow reuse of addresses and ports
	r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

	#Bind the socket to the server
	r.bind(('',PORT))
	
	#inet_pton - convert the IPv4 address from text to binary
	group_bin=socket.inet_pton(socket.AF_INET, MYGROUP_4)

	#mreq - defines the multicast group and interface to join
	#INADDR_ANY - receives listen on default multicast interface
	mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)

	#Join multicast - add the socket on the IPv4 multicast address of the selected interface.
	# 		IPPROTO_IP - IPv4 protocol	
	# 		IP_ADD_MEMBERSHIP - add the socket to the multicast group

	# Drop multicast - drop the socket from the IPv4 multicast address of the selected interface. Use the same primitive and replace IP_ADD_MEMBERSHIP  by
	# 		IP_DROP_MEMBERSHIP - drop the socket from the multicast group
	r.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

	txd_flag = True
	while True :
		rxd_data, sender = r.recvfrom(MSG_SIZE)
		pkt_rxd = json.loads(rxd_data.decode('utf-8'))
		if (app_conf.debug_multicast):
			print('STATUS: Packet received - THREAD: multicast_rxd - NODE: {}'.format(node),' - MSG: {}'.format(pkt_rxd),'\n')
		if (its_conf.physical_model):
			txd_flag = physical_layer_emulation (node_interface, coordinates, pkt_rxd)
		if (txd_flag):
			if (pkt_rxd['msg_type'] == 'BEACON'):
				beacon_rxd_queue.put(pkt_rxd)
			else:
				multicast_rxd_queue.put(pkt_rxd)
			if (app_conf.debug_physical_layer):
				print('STATUS: Packet delivered to upper layer - THREAD: multicast_rxd - NODE: {}'.format(node),' - MSG: {}'.format(pkt_rxd),'\n')
	return


def physical_layer_emulation (node_interface, coordinates, pkt_rxd):

	if (pkt_rxd['node'] == node_interface['node_id']):
		return True

	sender_distance = distance (coordinates, pkt_rxd)
	sender_range = range_type (pkt_rxd['node_type'])

	return (region (sender_distance, sender_range))

	
def distance (coordinates, pkt_rxd):
	x1 = coordinates['x']
	y1 = coordinates['y']
	x2 = pkt_rxd['pos_x']
	y2 = pkt_rxd['pos_y']
	return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def range_type (sender_type):
	if (sender_type==map.obu_node):
		return map.obu_range
	elif (sender_type==map.rsu_node):
		return  map.rsu_range
	elif (sender_type==map.au_node):
		return  map.rsu_range

def region (distance, range):

	min_range = its_conf.range_scale*range
	if distance > range:
		return False
	elif distance < min_range:
		return True
	else:
		txd_probablility = random.randint(1, 10)
		if txd_probablility < its_conf.drop_threshold:
			return False
		else:
			return True