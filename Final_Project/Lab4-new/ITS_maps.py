#!/usr/bin/env python

#################################################
## RSU | OBU | AU
#################################################

# node type
rsu_node = 1
obu_node = 2


# Node sub_types
rsu_park_sub_type = 'park_entry'

obu_sub_type1 = 'car'

#################################################
## PHYSICAL PROPERTIES
#################################################
rsu_range = 4000
obu_range = 3000

#################################################
## MAP
#################################################
map = {
    # RSU parking permission
    "11": {'type': rsu_node, 'sub_type': rsu_park_sub_type, 'x': 200, 'y': -200, 'status': 'inactive'},

    # OBU (car)
    "7": {'type': obu_node, 'sub_type': obu_sub_type1, 'x': 100, 'y': 0, 'speed': 20, 'direction': 'f', 'heading': 'S', 'status': 'inactive'},
    "8": {'type': obu_node, 'sub_type': obu_sub_type1, 'x': 100, 'y': -300, 'speed': 1, 'direction': 'f', 'heading': 'S', 'status': 'inactive'},
}

#################################################
## VISUALIZATION DASHBOARD
#################################################
visual = 0
size_x = 8000
size_y = 8000
