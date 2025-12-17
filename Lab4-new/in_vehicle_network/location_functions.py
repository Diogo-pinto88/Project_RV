#!/usr/bin/env python
# #################################################
## FUNCTIONS USED IN VEHICLE - (x,y) location
#################################################
import time, sys, os
from in_vehicle_network.car_motor_functions import get_vehicle_info
import in_vehicle_network.obd2 as obd2
import application.app_config as app_conf
from in_vehicle_network.conversion import *
import json


sys.path.append(os.path.abspath(".."))
import ITS_options as its_conf


#space_travelled =    [8, 16, 24, 32, 40], [2, 4, 6, 8, 10]

#------------------------------------------------------------------------------------------------
# position_update - updates x,y,t based on the current position, direction and heading. 
#       Note: No speed ot real behaviour of the vehicles is included
#       TIP: you can add here your position_update function. But, keep the parameters updated
#------------------------------------------------------------------------------------------------
def position_update(coordinates, node_interface, visual):

    init_node = 1
    active  = 1
    idle = 0

    speed, direction, heading=get_vehicle_info(node_interface)
    

    x=coordinates['x']
    y=coordinates['y']
    
    aux_dict = {}

    if (node_interface['vehicle_status']!=obd2.moving):
        return 
    current_time=time.time()
    delta_t=current_time-node_interface['time']

    node_interface['time']=current_time

    speed=node_interface['speed']
    node_id = node_interface['node_id']
    
    
    if (direction=='f'):
        distance = space_travelled[0][int(speed/20)-1]
    else:
        distance = space_travelled[1][int(speed/20)-1]   
    space=distance*delta_t

    if (its_conf.fixed_spaces): space=its_conf.delta_space


    if (((heading=='E') and (direction=='f')) or ((heading=='O') and (direction=='b'))):
        x=coordinates['x'] + space
        y=coordinates['y']
    elif (((heading=='E') and (direction=='b')) or ((heading=='O') and (direction=='f'))):
         x=coordinates['x'] - space
         y=coordinates['y']
    elif (((heading=='N') and (direction=='f')) or ((heading=='S') and (direction=='b'))):
        x=coordinates['x']
        y=coordinates['y'] + space
    elif (((heading=='N') and (direction=='b')) or ((heading=='S') and (direction=='f'))):
        x=coordinates['x']
        y=coordinates['y'] - space  
  
    coordinates.update({'x':x, 'y':y, 't':current_time})

    if visual:
        record_to_file = str(node_id) + ',' + 'obu' + ',' + str(coordinates['x']) + ',' + str(coordinates['y'])+ ',' + str (speed) + ',' + direction + ',' + heading
        print (record_to_file)                                  
        # aux_dict = {"node_id": node_id, "status ": init_node, "node_type": 'obu', "x": coordinates['x'], "y": coordinates['y'], "t": coordinates['t'], "speed": obd_2_interface['speed'], "direction": obd_2_interface['direction'], "heading": obd_2_interface['heading'], "command:": 'init_vehicle' }
        with open('../log_visual.json', 'a') as arquivo:
            arquivo.write(record_to_file)
            arquivo.write('\n')
             

   
    if (app_conf.debug_location):
        print ('update location: x = ', coordinates['x'], '   y = ', coordinates['y'], '  time = ', coordinates['t'])

    return


#------------------------------------------------------------------------------------------------
# position_read - last known position
#------------------------------------------------------------------------------------------------
def old_position_read(coordinates):

    x=coordinates['x']
    y=coordinates['y']
    t=coordinates['t']

    return x,y,t
