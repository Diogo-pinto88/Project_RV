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

    speed, direction, heading = get_vehicle_info(node_interface)

    # --- FIX: keep time updated even when not moving ---
    current_time = time.time()

    # update time references always
    node_interface['time'] = current_time
    coordinates['t'] = current_time

    # DEBUG (optional) - helps confirm vehicle_status changes when you press f/s
    if (app_conf.debug_location):
        print("[GPS] status=", node_interface.get('vehicle_status'),
              "speed=", node_interface.get('speed'),
              "dir=", direction, "heading=", heading)

    # if not moving, do not change x,y (only time)
    if node_interface.get('vehicle_status') != obd2.moving:
        # IMPORTANT: keep last_move_time updated even when stopped
        # so delta_t doesn't accumulate while the vehicle is stopped
        node_interface['last_move_time'] = current_time
        return
    # ---------------------------------------------------

    x = coordinates['x']
    y = coordinates['y']

    delta_t = current_time - node_interface.get('last_move_time', current_time)
    node_interface['last_move_time'] = current_time

    speed = node_interface['speed']

    # --- FIX: protect speed index ---
    sp = max(20, min(100, int(speed)))
    idx = max(0, int(sp/20) - 1)
    # -------------------------------

    if (direction == 'f'):
        distance = space_travelled[0][idx]
    else:
        distance = space_travelled[1][idx]

    space = distance * delta_t
    if (its_conf.fixed_spaces):
        space = its_conf.delta_space

    if (((heading=='E') and (direction=='f')) or ((heading=='O') and (direction=='b'))):
        x = coordinates['x'] + space
    elif (((heading=='E') and (direction=='b')) or ((heading=='O') and (direction=='f'))):
        x = coordinates['x'] - space
    elif (((heading=='N') and (direction=='f')) or ((heading=='S') and (direction=='b'))):
        y = coordinates['y'] + space
    elif (((heading=='N') and (direction=='b')) or ((heading=='S') and (direction=='f'))):
        y = coordinates['y'] - space

    coordinates.update({'x': x, 'y': y, 't': current_time})

    if (app_conf.debug_location):
        print('update location: x=', coordinates['x'], 'y=', coordinates['y'], 't=', coordinates['t'])

    return



#------------------------------------------------------------------------------------------------
# position_read - last known position
#------------------------------------------------------------------------------------------------
def old_position_read(coordinates):

    x=coordinates['x']
    y=coordinates['y']
    t=coordinates['t']

    return x,y,t
