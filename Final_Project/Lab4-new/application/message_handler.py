#!/usr/bin/env python
# ##########################################################################
## FUNCTIONS USED BY APPLICATION LAYER TO TRIGGER C-ITS MESSAGE GENERATION
# ##########################################################################
import datetime, time
import application.app_config as app_conf

import ITS_maps as map
import application.app_config as app_conf
import application.app_config_obu as app_obu_conf
import application.app_config_rsu as app_rsu_conf


#------------------------------------------------------------------------------------------------
# trigger_ca -trigger the generation of CA messages- Funcao nao usada!
#       (out) - time between ca message generation
#-------------------------------------------------------------------------------------------------
def trigger_ca(node):
	trigger_node=-1
	while trigger_node!= node:
		trigger_node  = input (' CA message - node id >   ')
	ca_user_data  = input ('\nCA message - Generation interval >   ')
	ca_user_data=10
	return int(ca_user_data)

#------------------------------------------------------------------------------------------------
# trigger_even -trigger an event that will generate a DEN messsge
#       (out) - event message payload with: 
#						type: 'start' - event detection OU + 'stop'  - event termination 
#						rep_interval - repetition interval of the same DEN message; 0 for no repetiion
#						n_hops - maximum number of hops that the message can reach
#						(roi_x, roi_y) 
#-------------------------------------------------------------------------------------------------
def trigger_event(node_type, event_number, event_status):

	if (node_type == map.obu_node):
		event_type = app_obu_conf.event_type[event_number]
		if event_status == app_obu_conf.status[event_number]:
			rep_interval = app_obu_conf.rep_interval[event_number] 
			n_hops = app_obu_conf.n_hops[event_number]
			roi_x  = app_obu_conf.roi_x[event_number] 
			roi_y  = app_obu_conf.roi_y[event_number]
			latency = app_obu_conf.latency[event_number]
	elif  (node_type == map.rsu_node):
		if (event_type == app_rsu_conf.event_type[event_number]):
			rep_interval = app_rsu_conf.rep_interval[event_number] 
			n_hops = app_rsu_conf.n_hops[event_number]
			roi_x  = app_rsu_conf.roi_x[event_number] 
			roi_y  = app_rsu_conf.roi_y[event_number]
			latency = app_rsu_conf.latency[event_number]
	event_msg={'event_type': event_type, 'event_status': event_status, 'rep_interval':int(rep_interval), 'n_hops': int(n_hops), 'roi_x':int(roi_x), 'roi_y': int(roi_y), 'latency':int(latency)}
	return event_msg


#------------------------------------------------------------------------------------------------
# spat_generation - generation of SPAT messages- 
#       used to announce the timings of TLS messages 
#-------------------------------------------------------------------------------------------------
def spat_generation(rsu_interface):
		
	if rsu_interface["type"] == map.rsu_node:
		node = rsu_interface.get("node_id")
		spat = {
       	 	"intersectionID": rsu_interface.get("node_id"), 
			"moy": calculate_moy(),
       		"statusFlags": rsu_interface["rsu_status"],
			"signalGroups":rsu_interface.get("tls_group"),
				"movement": rsu_interface.get("movement", []),
       	 		"priorityInformation": {
					"priorityRequest": False
       	 		}
   			}
	
	return spat

#------------------------------------------------------------------------------------------------
# ivim_generation -    Creates an IVIM message based on the type of situation.   
#    Parameters:
#    - event_type Type of situation (e.g., "speed_limit", "work_zone", "low_emission_zone")
#    - zone_id Zone identifier
#    - lat: Latitude of the zone
#    - lon: Longitude of the zone
#    - radius: Radius of the zone (in meters)
#    - start_date: Start date of the message validity (e.g., "2024-10-21T08:00:00")
#    - end_date End date of the message validity (e.g., "2024-10-21T18:00:00")
#    - kwargs: Additional parameters for each type of situation
#        - For speed limits: limite_velocidade
#        - For low emission zones: tipos_veiculos_permitidos
#        - For work zones: limite_velocidade_obras, sinal_obra    
#    Returns:
#   - Dictionary representing the IVIM message.
#------------------------------------------------------------------------------------------------
def ivim_containers_creation(rsu_interface, situation_type):
	
	node_type = rsu_interface["type"]
	node = rsu_interface["node_id"]

	
	if (node_type == map.rsu_node):
		if situation_type == "vehicle":
			vehicle_type = app_rsu_conf.vehicle_type
			ivim=ivim_vehicle (situation_type, vehicle_type)
		elif situation_type == "road_works":
			work_zone_type = app_rsu_conf.working_zone_type
			work_zone_status = app_rsu_conf.work_zone_status
			ivim=ivim_roadworks(situation_type, work_zone_type, work_zone_status)
		elif situation_type == "road_sign":
			sign_type = app_rsu_conf.sign_type
			x = app_rsu_conf.sign_x
			y = app_rsu_conf.sign_y
			ivim=ivim_roadsign (situation_type, sign_type, x, y)
		elif situation_type == "lane_condition":
			lane_id = app_rsu_conf.lane_id
			lane_type = app_rsu_conf.lane_type
			lane_status = app_rsu_conf.lane_status
			lane_restrictions = app_rsu_conf.lane_restrictions
			length = app_rsu_conf.restriction_length
			ivim=ivim_lane_condition (situation_type, lane_id, lane_status, lane_type, lane_restrictions, length)
		elif situation_type == "speed_limit":
			zone_type = app_rsu_conf.zone_type
			default_speed = app_rsu_conf.default_speed
			applicable_speed = app_rsu_conf.applicable_speed
			zone_speed = app_rsu_conf.zone_speed
			ivim=ivim_speed_limit(situation_type, zone_type, default_speed, applicable_speed, zone_speed)
		elif situation_type == "weather_condition":
			weather_condition = app_rsu_conf.condition
			visibility = app_rsu_conf.visibility
			road_condition = app_rsu_conf.road_surface
			ivim=ivim_weather_information (situation_type, weather_condition, visibility, road_condition)
		else:
			print ("error: unnkown ivim situation")
			ivim ={}
		return ivim

#------------------------------------------------------------------------------------------------
# position_node - retrieve nodes's position from the message
#------------------------------------------------------------------------------------------------
def position_node(msg):
	
	x=msg['pos_x']
	y=msg['pos_y']
	t=msg['time']

	return x, y, t


#------------------------------------------------------------------------------------------------
# movement_node - retrieve nodes's dynamic information from the message
#------------------------------------------------------------------------------------------------
def movement_node(msg):
	
	s=msg['speed']
	d=msg['dir']
	h=msg['heading']

	return s, d, h

#------------------------------------------------------------------------------------------------
# calculate_moy - calculate the minute of the year time measurement. MOY represents a specific minute within the entire calendar year, allowing precise synchronization of traffic signal timing and status. 
#------------------------------------------------------------------------------------------------

def calculate_moy():
	now = datetime.datetime.now()
	day_of_year = now.timetuple().tm_yday
	minutes_today = now.hour * 60 + now.minute
	moy = (day_of_year - 1) * 1440 + minutes_today

	return moy


def ivim_vehicle(situation_type, vehicle_type):

	ivim_message = {
		"msg_sub_type": situation_type,
		# type: not applicable (-1) emergency_vehicle=1, breakdown_vehicle=2, danger_goods_vehicle=3, ...
		"vehicle_information": {
        	"type": vehicle_type
    	}
	}
	return ivim_message 

def ivim_roadworks (situation_type, work_zone_type, work_zone_status):
#work_zone_type: 'road_repair', 'bridge_maintenance'
#work_zone_status: 'active', 'inactive'
	ivim_message = {
		"msg_sub_type": situation_type,
		"roadwork_information": {
       	 	"work_zone_type": work_zone_type,  
        	"work_zone_status": work_zone_status, 
   		}
	}
	return ivim_message 

def ivim_roadsign (situation_type, sign_type, x, y):
#sign_type: 'speed_limit', 'stop' 'pedestrian_crossing' 'yield' 'end'
	
	ivim_message = {
		"msg_sub_type": situation_type,
        "sign_type": sign_type,
            "sign_position": {
                "x": x,
                "y": y
            }
        }
	return ivim_message 

def ivim_lane_condition(situation_type, lane_id, status, lane_type, lane_restrictions, length):
#lane_status: 'closed', 'open', 'merging'
#lane_type: 'normal'  'bus' 'bike' 'mixed' 'high-ocuppancy-vehicles' 
#lane_restrictions = 'none' 'no_overtaking' 'heigh_limit'  'merge_left', 'merge_right'
	ivim_message = {
		"msg_sub_type": situation_type,
		"lane_unformation": 
        {
            "lane_id": lane_id,
            "lane_status": status,
            "lane_type": lane_type,
            "lane_restrictions": lane_restrictions,
			"restriction_length": length
        }
	}
	return ivim_message
		
def ivim_speed_limit (situation_type, zone_type, default_speed, applicable_speed, zone_speed):
# type: urban, highway, rural, unknown (-1)

	ivim_message = {
		"msg_sub_type": situation_type,
		"speed_limit_information": {
        	"default_speed_limit": {
            	"type": zone_type,
            	"speed": default_speed  
        	},
        	"work_zone_speed_limit": {
            	"applicable": applicable_speed,
            	"speed": zone_speed   
        	}
    	}
	}
	return ivim_message 

def ivim_weather_information(situation_type, weather_condition, visibility, road_condition):
#condition: +rain', 'slippery', 'fog' 'snow'
#visibility = rain or fog: visibility=  0-100%. slippery: visibility=  -1 (not applicable)
#road_surface: 'dry', 'wet', 'icy' 'normal' 

	ivim_message = {
		"msg_sub_type": situation_type,
		"weather_information": {
        	"condition": weather_condition,
        	"visibility": visibility,
       	 "roadSurfaceCondition": road_condition
   		 }
	}
	return ivim_message 

#------------------------------------------------------------------------------------------------
# trigger_even -trigger an event that will generate a DEN messsge
#       (out) - event message payload with: 
#						type: 'start' - event detection OU + 'stop'  - event termination 
#						rep_interval - repetition interval of the same DEN message; 0 for no repetiion
#						n_hops - maximum number of hops that the message can reach
#						(roi_x, roi_y) 
#-------------------------------------------------------------------------------------------------
def trigger_situation(situation_status):
	
	if situation_status == 'start':
		rep_interval = app_rsu_conf.ivim_generation_interval
		n_hops = app_rsu_conf.ivim_n_hops
		roi_x  = app_rsu_conf.ivim_roi_x
		roi_y  = app_rsu_conf.ivim_roi_y
		latency = app_rsu_conf.ivim_latency
	situation_msg={'situation_status': situation_status,'rep_interval':int(rep_interval), 'n_hops': int(n_hops), 'roi_x':int(roi_x), 'roi_y': int(roi_y), 'latency':int(latency)}

	return situation_msg

def ivim_message_received (msg_rxd):
			
	use_case = msg_rxd['situation']['msg_sub_type']
	if (use_case == 'vehicle'):
		situation = msg_rxd['situation']['vehicle_information']
	elif (use_case=='road_works'):
		situation = msg_rxd['situation']['roadwork_information']
	elif (use_case=='weather_condition'):
		situation = msg_rxd['situation']['weather_information']

	return use_case, situation