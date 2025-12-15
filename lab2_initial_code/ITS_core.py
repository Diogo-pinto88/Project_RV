#!/usr/bin/env python
from socket import *
import sys, time
from threading import Thread, Event
from Queue import *

# PROTOCOL STACK - One folder per layer of VANET protocol stack. It may include more than one entity. Each entity is a different thread.
# VANET protocol stack data link layer - multicast communication - basic emulation of logical and link layer communication.
from data_link.multicast import *

# VANET protocol stack transport & network layer - it may include: topology management, information dissemination within a ROI, location-based routing
from transport_network.geonetworking import *

# VANET protocol stack facilities layer (common services to all applications)- it may include: cooperative awareness messages, event management message
from facilities.common_services import *

# VANET protocol stack application layer - application business logic
from application.obu_application import *
from application.rsu_application import *
from application.au_application import *

# OBU-interface with vehicles - it may include: car motor control funtions, other sensors/actuator interfaces, location information
from in_vehicle_network.car_control import *

# RSU interface with legacy systems - it may include: traffic light control funtions, other sensors/actuator interfaces, location information
from rsu_legacy_systems.rsu_control import *

# Physical map representation and nodes used.
import ITS_maps as maps
import ITS_options as its_conf

# QUEUES - used to tranfer messages between adjacent layers of the protocol stack
my_system_rxd_queue=Queue()
movement_control_txd_queue=Queue()
rsu_control_txd_queue=Queue()
ca_service_txd_queue=Queue()
den_service_txd_queue=Queue()
spat_service_txd_queue=Queue()
map_service_txd_queue=Queue()
ivim_service_txd_queue=Queue()

services_rxd_queue=Queue()


geonetwork_txd_queue=Queue()
geonetwork_rxd_ca_queue=Queue()
geonetwork_rxd_den_queue=Queue()

geonetwork_rxd_spat_queue=Queue()
geonetwork_rxd_map_queue=Queue()
geonetwork_rxd_ivim_queue=Queue()


beacon_rxd_queue=Queue()

multicast_txd_queue=Queue()
multicast_rxd_queue=Queue()

# EVENTS  -  flags used to coordinate threads activities
# start_flag - set when all threads started to triggered the execution of each thread logic
start_flag=Event()


# VARIABLES  -  shared by different threads
# coordinates - dictionary with node's location in the format (x,y,time)
coordinates = dict()
# node_interface - dictionary with the node's status information
# OBU (vehicle) - node_id, node_type, node_subtype, speed, direction, heading, current_time, plus_info (optional)
# RSU (traffic ligh system): node_id, node_type, node_subtype, num_tls, tls_group: (id, state, start, end), movement: (direction, pedestrian_detection)
# AU (person)
node_interface = dict()


# INPUT ARGUMENTS
# node_id
##################################################
## MAIN-ITS_core
##################################################

def main(argv):
	global node_interface, coordinates
	
	if (len(argv)<2):
		print('ERROR: Missing arguments: node_id, flag')
		sys.exit()
	else:
		node_id = argv[1]
		#visual = argv[2]
		visual = False
		current_time = repr(time.time())
		if node_id in maps.map:
			coordinates = {'x':maps.map[node_id]['x'], 'y':maps.map[node_id]['y'], 't': current_time}
			node_type = maps.map[node_id]['type']
			node_sub_type =  maps.map[node_id]['sub_type']
			if (node_sub_type == 'car') or (node_sub_type == 'tls'):
				plus_info = ''
			else:
				plus_info=maps.map[node_id]['plus_info']
			maps.map[node_id]['status'] = 'ready'
			if node_type == maps.obu_node:
				speed = maps.map[node_id]['speed']
				direction = maps.map[node_id]['direction']
				heading = maps.map[node_id]['heading']
				node_interface={'node_id': node_id, 'type':node_type, 'sub_type': node_sub_type, 'speed': speed, 'direction': direction, 'heading': heading, 'plus_info': plus_info, 'time': current_time}
			else:
				if (node_sub_type == 'tls'):
					node_interface={'node_id':node_id, 'type':node_type, 'num_tls': maps.map[node_id]['num_tls'],'tls_group': maps.map[node_id]['tls_groups'], 'movement': maps.map[node_id]['movement'], 'plus_info': plus_info, 'time': current_time }
				else:
					exit()
	
	threads=[]

	try:

		##################################################
		#  Arguments common to all threads:
		#      node_id: node identification
		#      startFlag: status event that indicates that all threads were launched and can start execution
		##################################################

		##################################################
		#     Application layer threads
		##################################################

		if (node_type==maps.obu_node):
			# Thread - 	  	obu_application_txd: create and send messages from the OBU to other nodes
			# Arguments -	node_interface: dictionary that contains the current status of the OBU
			# 			 	start_flag: thread execution control flag
			#            	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			# 			  	ca_service_txd_queue: queue to send data to ca_services_txd
			#             	den_service_txd_queue: queue to send data to den_services_txd
			t=Thread(target=obu_application_txd, args=(node_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue,))
			t.start()
			threads.append(t)
	

			# Thread - 		obu_application_rxd: receive data from services_rxd, process it and send it to the cars/rsu/persons
			# Arguments - 	node_interface: dictionary that contains the current status of the OBU
			# 			 	start_flag: thread execution control flag
			#             	services_rxd_queue: queue to get data from ca_service_rxd or den_service_rxd
			#             	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			t=Thread(target=obu_application_rxd, args=(node_interface, start_flag, services_rxd_queue, my_system_rxd_queue,))
			t.start()
			threads.append(t)
	

			# Thread - 		obu_system: business logic 
			# Arguments - 	node_interface: dictionary that contains the current status of the OBU
			# 			 	start_flag: thread execution control flag
			# 			  	coordinates: last known coordinates
			#  			  	my_system_rxd_queue: queue to receive data from other application layer threads relevant for business logic decision-process 
			#             	movement_control_txd_queue: queue to send commands to control vehicles movement
			t=Thread(target=obu_system, args=(node_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue,))
			t.start()
			threads.append(t)
	
		if (node_type==maps.rsu_node):
			# Thread -    	rsu_application_txd: create and send messages from the RSU to other nodess
			# Arguments - 	node_interface: dictionary that contains the current status of the RSU
			# 			 	start_flag: thread execution control flag
			#             	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			# 			  	ca_service_txd_queue: queue to send data to ca_services_txd
			#             	den_service_txd_queue: queue to send data to den_services_txd
			t=Thread(target=rsu_application_txd, args=(node_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue, spat_service_txd_queue, ivim_service_txd_queue,))
			t.start()
			threads.append(t)
	

			# Thread - 		rsu_application_rxd: receive data from services_rxd, process it and send it to the cars/rsu/persons
			# Arguments - 	node_interface: dictionary that contains the current status of the RSU
			# 			 	start_flag: thread execution control flag
			#			  	car movement: controls the car movement
			#             	services_rxd_queue: queue to get data from ca_service_rxd or den_service_rxd
			#             	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			t=Thread(target=rsu_application_rxd, args=(node_interface, start_flag, services_rxd_queue, my_system_rxd_queue,))
			t.start()
			threads.append(t)
	
			# Thread - 		rsu_system: business logic 
			# Arguments - 	node_interface: dictionary that contains the current status of the RSU
			# 			 	start_flag: thread execution control flag
			# 			  	coordinates: last known coordinates
			#	   		  	my_system_rxd_queue: queue to receive data from other application layer threads relevant for business logic decision-process 
			#             	movement_control_txd_queue: queue to send commands to control vehicles movement
			t=Thread(target=rsu_system, args=(node_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue,))
			t.start()
			threads.append(t)

		if (node_type==maps.au_node):
			# Thread -    	au_application_txd: create and send messages from the AU to other nodess
			# Arguments - 	node_interface: dictionary that contains the current status of the AU
			# 			 	start_flag: thread execution control flag
			#             	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			# 			  	ca_service_txd_queue: queue to send data to ca_services_txd
			#             	den_service_txd_queue: queue to send data to den_services_txd
			t=Thread(target=au_application_txd, args=(node_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue,))
			t.start()
			threads.append(t)
	

			# Thread - 		au_application_rxd: receive data from services_rxd, process it and send it to the cars/rsu/persons
			# Arguments - 	node_interface: dictionary that contains the current status of the AU
			# 			 	start_flag: thread execution control flag
			#             	services_rxd_queue: queue to get data from ca_service_rxd or den_service_rxd
			#             	my_system_rxd_queue: queue to send data to my_system that is relevant for business logic decision-process 
			t=Thread(target=au_application_rxd, args=(node_interface, start_flag, services_rxd_queue, my_system_rxd_queue,))
			t.start()
			threads.append(t)
	

			# Thread - 		au_system: business logic 
			# Arguments - 	node_interface: dictionary that contains the current status of the AU
			# 			 	start_flag: thread execution control flag
			# 			  	coordinates: last known coordinates
			#			  	my_system_rxd_queue: queue to receive data from other application layer threads relevant for business logic decision-process 
			#             	movement_control_txd_queue: queue to send commands to control vehicles movement
			t=Thread(target=au_system, args=(node_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue,))
			t.start()
			threads.append(t)

		##################################################
		#     Facilities layer threads
		##################################################

		# Thread - 		ca_service_rxd: receive data from application_txd, generates cooperative awaraness and sends the CA message to the geonetwork_txd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		#             	ca_services_txd_queue: queue to get data from application_txd
		#             	geonetwork_txd_queue: queue to send data to geonetwork_txd
		t=Thread(target=ca_service_txd, args=(node_interface, start_flag, coordinates, ca_service_txd_queue, geonetwork_txd_queue,))
		t.start()
		threads.append(t)

		# Thread - 		ca_service_rxd: receive data from geonetwork_rxd, process the CA message and send the result to the application_rxd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				geonetwork_rxd_ca_queue: queue to get data from geonetwork_rxd
		#             	services_rxd_queue: queue to send data to application_rxd
		t=Thread(target=ca_service_rxd, args=(node_interface, start_flag, geonetwork_rxd_ca_queue, services_rxd_queue,))
		t.start()
		threads.append(t)

		# Thread -  	den_service_txd: receive data from application_txd, generates events and sends the DEN message to the geonetwork_txd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				coordinates: last known coordinates
		#             	den_services_txd_queue: queue to get data from application_txd
		#            	geonetwork_txd_queue: queue to send data to geonetwork_txd
		t=Thread(target=den_service_txd, args=(node_interface, start_flag, coordinates, den_service_txd_queue, geonetwork_txd_queue,))
		t.start()
		threads.append(t)

		# Thread - 		den_service_rxd: receive data from geonetwork_rxd, process the DEN message and send the result to the application_rxd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				geonetwork_rxd_den_queue: queue to get data from geonetwork_rxd
		#             	services_rxd_queue: queue to send data to application_rxd
		#             	services_txd_queue: queue to relay data to geonetwork_txd in case of multi-hop communication
		t=Thread(target=den_service_rxd, args=(node_interface, start_flag, geonetwork_rxd_den_queue, services_rxd_queue, geonetwork_txd_queue, ))
		t.start()
		threads.append(t)

		if (node_type==maps.rsu_node):
			# Thread -  	spat_service_txd: receive data from application_txd, generates events and sends the SPaT message to the geonetwork_txd
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				coordinates: last known coordinates
			#             	spat_services_txd_queue: queue to get data from application_txd
			# #           	geonetwork_txd_queue: queue to send data to geonetwork_txd
			t=Thread(target=spat_service_txd, args=(node_interface, start_flag, coordinates,  spat_service_txd_queue, geonetwork_txd_queue,))
			t.start()
			threads.append(t)

		if (node_type!=maps.rsu_node):
			# Thread - 		spat_service_rxd: receive data from geonetwork_rxd, process the SPaT message and send the result to the application_rxd
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				geonetwork_rxd_spat_queue: queue to get data from geonetwork_rxd
			#             	services_rxd_queue: queue to send data to application_rxd
			t=Thread(target=spat_service_rxd, args=(node_interface, start_flag, geonetwork_rxd_spat_queue, services_rxd_queue, ))
			t.start()
			threads.append(t)


		# Thread -  	map_service_txd: receive data from application_txd, generates events and sends the SPaT message to the geonetwork_txd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				coordinates: last known coordinates
		#             	map_services_txd_queue: queue to get data from application_txd
		#            	geonetwork_txd_queue: queue to send data to geonetwork_txd
		t=Thread(target=map_service_txd, args=(node_interface, start_flag, coordinates, map_service_txd_queue, geonetwork_txd_queue,))
		t.start()
		threads.append(t)

		# Thread	- 	map_service_rxd: receive data from geonetwork_rxd, process the SPaT message and send the result to the application_rxd
		# Arguments	- 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				geonetwork_rxd_map_queue: queue to get data from geonetwork_rxd
		#             	services_rxd_queue: queue to send data to application_rxd
		t=Thread(target=map_service_rxd, args=(node_interface, start_flag, geonetwork_rxd_map_queue, services_rxd_queue,))
		t.start()
		threads.append(t)

		if (node_type==maps.rsu_node) or (node_type==maps.au_node):
			# Thread -  	ivim_service_txd: receive data from application_txd, generates events and sends the SPaT message to the geonetwork_txd
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				coordinates: last known coordinates
			#             	ivim_services_txd_queue: queue to get data from application_txd
			#            	geonetwork_txd_queue: queue to send data to geonetwork_txd
			t=Thread(target=ivim_service_txd, args=(node_interface, start_flag, coordinates, ivim_service_txd_queue, geonetwork_txd_queue,))
			t.start()
			threads.append(t)

		if (node_type==maps.rsu_node) or (node_type==maps.obu_node):
			# Thread - 		ivim_service_rxd: receive data from geonetwork_rxd, process the SPaT message and send the result to the application_rxd
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				geonetwork_rxd_ivim_queue: queue to get data from geonetwork_rxd
			#             	services_rxd_queue: queue to send data to application_rxd
			t=Thread(target=ivim_service_rxd, args=(node_interface,  start_flag, geonetwork_rxd_ivim_queue, services_rxd_queue,))
			t.start()
			threads.append(t)


		##################################################
		#     Transport and network layer threads
		##################################################

		# Thread - 		geonetwork_txd: receive data from geoenetwork_txd, process the geonetwork information and send the result to the multicast_rxd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				geonetwork_txd_queue: queue to get data from ca_service_txd or den_service_txd
		#             	multicast_txd_queue: queue to send data to multicast_txd
		t=Thread(target=geonetwork_txd, args=(node_interface, start_flag, geonetwork_txd_queue, multicast_txd_queue,))
		t.start()
		threads.append(t)

		# Thread- 		geonetwork_rxd: receive data from multicast_rxd, process the geonetwork information and send the result to the services_rxd
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flag
		# 				coordinates: last known coordinates
		# 				multicast_rxd_queue: queue to get data from multicast_txd
		#             	geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue, geonetwork_rxd_spat_queue, geonetwork_rxd_ivim_queue: queue to send data to services_rxd, after being processed
		t=Thread(target=geonetwork_rxd, args=(node_interface, start_flag, multicast_rxd_queue, geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue, geonetwork_rxd_spat_queue, geonetwork_rxd_ivim_queue,))
		t.start()
		threads.append(t)

		if (its_conf.geonetwork_model):

			# Thread - 		beacon_txd: periodical generation of beacons
			# Arguments - 	coordinates: last known coordinates
			#             	multicast_txd_queue: queue to send beacons to multicast_txd
			t=Thread(target=beacon_txd, args=(node_interface, start_flag, coordinates, multicast_txd_queue,))
			t.start()
			threads.append(t)

			# Thread- 		geonetwork_rxd: receive data from multicast_rxd, process the geonetwork information and send the result to the services_rxd
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				multicast_rxd_queue: queue to get data from multicast_rxd
			#             	geonetwork_rxd_queue: queue to send data to services_rxd, after being processed
			t=Thread(target=beacon_rxd, args=(node_interface, start_flag, beacon_rxd_queue,))
			t.start()
			threads.append(t)

			# Thread- 		check_loc_table: check loc_table_entries and deleted outdated entries
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			t=Thread(target=check_loc_table, args=(node_interface, start_flag,))
			t.start()
			threads.append(t)


		##################################################
		#     Link layer threads
		##################################################

		# Thread - 		multicast_rxd: receive data from multicast socket, process and send the result to the geonetwork_rxd, after being processed, if needed
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				multicast_rxd_queue: queue to send data to geonetwork_rxd
		#            	beacon_rxd_queue: queue to send data to beacon_rxd
		t=Thread(target=multicast_rxd, args=(node_interface, start_flag, coordinates, multicast_rxd_queue, beacon_rxd_queue,))
		t.start()
		threads.append(t)

		# Thread - 		multicast_txd: receive data from geonetwork_txd and send it to the multicast socket
		# Arguments - 	node_interface: dictionary that contains the current node status 
		# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
		# 				multicast_txd_queue: queue to get data from transmission from geonetwork_txd
		t=Thread(target=multicast_txd, args=(node_interface, start_flag, multicast_txd_queue,))
		t.start()
		threads.append(t)

		if node_type == maps.obu_node:

		##################################################
		#     In-vehicles threads
		##################################################

			# Thread- 		update_location: update the node coordinates (x,y) to emulate the GPS device
			# Arguments - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				coordinates: dictionay with (x,y) coordinates and time instant t of measurement
			#           	node_interface: dictionary with the movement information of the car. 
			t=Thread(target=update_location, args=(node_interface, start_flag, coordinates, visual, ))
			t.start()
			threads.append(t)

			# Thread- movement control: to control the movement of the vehicles
			# Arguments  - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				coordinates: dictionay with (x,y) coordinates and time instant t of measurement
			#			  	node_interface: dictionary with the movement information of the car
			#			  	movement_control_txd_queue: fila que recebe os comandos para o controlo do carro a partir aplicacao.
			t=Thread(target=movement_control, args=(node_interface, start_flag, coordinates,  movement_control_txd_queue,))
			t.start()
			threads.append(t)
		else:
			# Thread- movement control: to control the movement of the vehicles
			# Arguments  - 	node_interface: dictionary that contains the current node status 
			# 			 	start_flag: thread execution control flagcoordinates: last known coordinates
			# 				coordinates: dictionay with (x,y) coordinates and time instant t of measurement
			#			 	rsu_control_txd_queue: fila que recebe os comandos para o controlo da rsa a partir da aplicacao.
			t=Thread(target=rsu_control, args=(node_interface, start_flag, coordinates,  rsu_control_txd_queue,))
			t.start()
			threads.append(t)
		
		start_flag.set()

	except:
		#exit the program if there is an error when opening one of the threads
		print('STATUS: Error opening one of the threads -  NODE: {}'.format(node_id),'\n')
		for t in threads:
			t.join()
			sys.exit()
	return

if __name__=="__main__":
	main(sys.argv[0:])
