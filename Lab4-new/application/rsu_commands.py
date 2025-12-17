#!/usr/bin/env python
# #####################################################################################################
# rsu_control comamnds: output test only with: single pin (led) and set of pind (traffic light)
#   Note: modifications required, for complex traffic light systems (with more than one semaphore)
#######################################################################################################
import application.app_config as app_conf

def start_rsu(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: start_rsu')

    rsu_control_msg="s"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def exit_rsu(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: exit_rsu')
    rsu_control_msg="x"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def turn_on(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: turn_on')
    rsu_control_msg="1"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def turn_off(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: turn_off')
    rsu_control_msg="0"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def green_tls(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: green_tls')
    rsu_control_msg="green"
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def yellow_tls(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: yellow_tls')
    rsu_control_msg="yellow" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def red_tls(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: red_tls')
    rsu_control_msg="red" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def intersection_update(rsu_control_txd_queue):
    if (app_conf.debug_app) or (app_conf.debug_rsu):
        print ('rsu_application: intersection_state updated')
    rsu_control_msg="ok" 
    rsu_control_txd_queue.put(rsu_control_msg)
    return    

def sem_id(rsu_control_txd_queue, data):
    rsu_control_msg=data
    rsu_control_txd_queue.put(rsu_control_msg)
    return 

def single_tls (tls, rsu_control_txd_queue):
    
    state = next(iter(tls.values()))['state']
    key = next(iter(tls))
    if (state=='green'):
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)
    elif (state=='yellow'):
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)
    elif (state=='red'):
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key)


def multiple_lane_tls(lane_tls, rsu_control_txd_queue):
    keys = list(lane_tls.keys())
    key_s1 = keys[0]
    key_s2 = keys[1]
    if (lane_tls[key_s1]['state']=='green'):
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='yellow'):
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='red'):
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)

    

def single_lane_tls(lane_tls, rsu_control_txd_queue):
    keys = list(lane_tls.keys())
    key_s1 = keys[0]
    key_s2 = keys[1]

    if (lane_tls[key_s1]['state']=='green'):
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        yellow_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='yellow'):
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        red_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)
    elif (lane_tls[key_s1]['state']=='red'):
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s1)
        green_tls(rsu_control_txd_queue)
        sem_id(rsu_control_txd_queue, key_s2)

def junction_tls (tls_group, rsu_control_txd_queue):
   
    first_lane_tls = dict(list(tls_group.items())[:2])
    second_lane_tls = dict(list(tls_group.items())[-2:])
    state = next(iter(first_lane_tls.values()))["state"]
    if (state=='green'):
        single_lane_tls(first_lane_tls, rsu_control_txd_queue)
        single_lane_tls(second_lane_tls, rsu_control_txd_queue)
    else:
        single_lane_tls(second_lane_tls, rsu_control_txd_queue)
        single_lane_tls(first_lane_tls, rsu_control_txd_queue)



     