#!/usr/bin/env python

#################################################
## RSU | OBU | AU
#################################################

#------------------------------------------------
# node type
#------------------------------------------------
rsu_node = 1
obu_node = 2
au_node = 3

#------------------------------------------------
# Node sub_types
#------------------------------------------------
# RSU : 'tls' | 'toll' | 'park_entry' | <other...>
rsu_sub_type = 'tls'
# OBU : 'car' | 'truck' | 'police' | 'emergency' | 'bus' | 'bike' | <other...>
obu_sub_type1 = 'car'
obu_sub_type2 = 'emergency'

#################################################
## PHYSICAL PROPERTIES
#################################################
#------------------------------------------------
# Antennas range
#------------------------------------------------
rsu_range = 4000
obu_range = 3000
au_range = 1000



#################################################
## MAP - 
#################################################
#------------------------------------------------
# Road network
# ------------------------------------------------
#road_net = {
#    'h_road': {'h1': {'x_in': int(-size_x / 2), 'y_in': 0, 'x_out': int(size_x / 2), 'y_out': 0},
#               'h2': {'x_in': int(-size_x / 2), 'y_in': int(size_y / 4), 'x_out': int(size_x / 2), 'y_out': int(size_y / 4)},
#    },
#    'v_road': {'v1': {'x_in': 0, 'y_in': int(-size_y / 2), 'x_out': 0, 'y_out': int(size_y / 2)},
#              'v2': {'x_in': 0, 'y_in': int(-size_y / 4), 'x_out': 0, 'y_out': int(size_y / 4)}
#    }
#}

#------------------------------------------------
# Virtual map
# ------------------------------------------------
map = {"6":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x':   25,  'y': 1000,    'speed':100,   'direction':'f',  'heading':'S',  'status': 'inactive'},
       "7":{'type':  obu_node,  'sub_type': obu_sub_type1, 'x':   25,  'y':-1000,    'speed':100,   'direction':'f',  'heading':'N',  'status': 'inactive'}
      }


#################################################
## VISUALIZATION DASHBOARD
#################################################
visual = 0
size_x = 8000
size_y = 8000