#!/usr/bin/env python
# #####################################################################################################
# APP CONFIGURATION PARAMETERS -
#######################################################################################################


#------------------------------------------------------------------------------------------
#include here any specific configuration of the application
#------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------
# Traffic light control
#-----------------------------------------------------------------------------------------

#definir aqui a informacao necessaria à configuracao duma RSU.
# Por exemplo: numero de semaforos. Ruas e faixas que cada semaforo controla. estado de cada semaforo, etc...


#definir aqui a informacao necessaria à configuracao duma RSU.
# Por exemplo: numero de semaforos. Ruas e faixas que cada semaforo controla. estado de cada semaforo, etc...
tls_timing = 10

# #####################################################################################################
# CA MESSAGES
# #####################################################################################################
warm_up_time = 10
spat_generation_interval = 10           #wait time between consecutive spat messages
ivim_generation_interval = 10           #wait time between consecutive ivim messages
ca_generation_interval = 5              #wait time between consecutive ca messages


# #####################################################################################################
# IVIM MESSAGES
# #####################################################################################################

#IVIM message groups

#Possible situations
#vehicle use case: 0
#vehicle_type: 'na' 'emergency_vehicle', 'breakdown_vehicle', 'hazardous_materials_transport'
vehicle_type = 'breakdown_vehicle'

#working zone use_case: 1
#work_zone_type: 'road_repair', 'bridge_maintenance'
working_zone_type = 'road_repair'
#work_zone_status: 'active', 'inactive'
work_zone_status = 'active'

#road sign use_case: 2
#sign_type: 'speed_limit', 'stop' 'pedestrian_crossing' 'yield' 'end'
sign_type = 'speed_limit'
sign_x = 10
sign_y = 10

#lane condition use_case: 3
lane_id = 1
#lane_status: 'closed', 'open', 'merging'
lane_status = 'closed'
#lane_type: 'normal'  'bus' 'bike' 'mixed' 'high-ocuppancy-vehicles' 
lane_type = 'normal'
#lane_restrictions = 'none' 'no_overtaking' 'heigh_limit'  'merge_left', 'merge_right' 
lane_restrictions = 'merge_left'
#restriction_length
restriction_length=100

#lane_id = 2
#lane_status: 'closed', 'open', 'merging'
#lane_status = 'open'
#lane_type: 'normal'  'bus' 'bike' 'mixed' 'high-ocuppancy-vehicles' 
#lane_type = 'normal'
#lane_restrictions = 'none' 'no_overtaking' 'heigh_limit'  'merge_left', 'merge_right'
#lane_restrictions = 'no_overtaking'
#restriction_length
#restriction_length=100
		
#ivim speed limite use_case: 4
# type: 'urban', 'highway', 'rural', 'unknown' (-1)
zone_type = 'urban'
default_speed = 70
applicable_speed = True
zone_speed = 30

#ivim speed limite use_case: 5
#condition: +rain', 'slippery', 'fog' 'snow'
condition = 'snow'
#visibility = rain or fog: visibility=  0-100%. slippery: visibility=  -1 (not applicable)
visibility = 70
#road_surface: 'dry', 'wet', 'icy' 'normal' 
road_surface = 'icy'



#if event_status == 'start':
# IVIM message - repetition interval (0 if single event)
ivim_rep_interval = 0
# IVIM message - Maximum hop number
ivim_n_hops = 8
# IVIM  message - ROI x coordinates (0 if none)
ivim_roi_x  = 0
# IVIM message - ROI y coordinates (0 if none)
ivim_roi_y  = 0
# IVIM message - ROI y coordinates (0 if none)
ivim_latency = 3600


safety_critical = 0
# DEN message - Event type
event_type = ["safety_critical_warning"]
# DEN message - Event status (start | update | stop)
event_status = ['start']
#if event_status == 'start':
#DEN message - repetition interval (0 if single event)
rep_interval = [0]
# DEN message - Maximum hop number
n_hops = [8]
#DEN message - ROI x coordinates (0 if none)
roi_x  = [0]
#DEN message - ROI y coordinates (0 if none)
roi_y  = [0]
#DEN message - ROI y coordinates (0 if none)
latency = 3600

 

 