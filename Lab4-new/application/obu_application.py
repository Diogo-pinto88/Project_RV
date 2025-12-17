#!/usr/bin/env python
# #####################################################################################################
# SENDING/RECEIVING APPLICATION THREADS - add your business logic here!
# Note: you can use a single thread, if you prefer, but be carefully when dealing with concurrency.
#######################################################################################################
from socket import MsgFlag
import time
import ITS_maps as map
from application.message_handler import *
from application.obu_commands import *
from facilities.services import create_den_message
import application.app_config as app_conf
import application.app_config_obu as app_obu_conf


#-----------------------------------------------------------------------------------------
# Thread: application transmission. 
#-----------------------------------------------------------------------------------------
def obu_application_txd(obd_2_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):

    while not start_flag.isSet():
        time.sleep (1)
    if (app_conf.debug_sys):
            print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(obd_2_interface["node_id"]),'\n')


#-----------------------------------------------------------------------------------------
# Thread: application reception. 
#-----------------------------------------------------------------------------------------
def obu_application_rxd(obd_2_interface, start_flag, services_rxd_queue, my_system_rxd_queue):

    while not start_flag.isSet():
        time.sleep (1)
    if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(obd_2_interface["node_id"]),'\n')
    
    while True :
          msg_rxd = services_rxd_queue.get()
          if msg_rxd['msg_type'] in ["SPAT", "IVIM"]:
               if (app_conf.debug_app_spat):
                    print ('\n....>obu_application - message received ', msg_rxd)
               my_system_rxd_queue.put(msg_rxd)


#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control 
#-----------------------------------------------------------------------------------------
def obu_system(obd_2_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue, den_service_txd_queue):

    while not start_flag.isSet():
        time.sleep (1)
    if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(obd_2_interface["node_id"]),'\n')
    
    # Init car 
    open_car(movement_control_txd_queue)
    turn_on_car(movement_control_txd_queue)
    # Start moving forward.
    car_move_forward(movement_control_txd_queue)

    while True :
        msg_rxd = my_system_rxd_queue.get()
        if (msg_rxd['msg_type'] == 'SPAT'):
            if 'intersection' in msg_rxd:
                tls_group = msg_rxd['intersection']['signalGroups']
                movement = msg_rxd['intersection']['movement']
                
                for key, value in movement.items():
                    direction = value['direction']
                    if (direction == obd_2_interface['heading']):
                        state = tls_group[key]['state']
                        if (state == 'red'):
                            stop_car (movement_control_txd_queue)
                        elif (state == 'yellow'):
                            car_move_very_slow (movement_control_txd_queue)
                        elif (state == 'green'):
                            car_move_forward(movement_control_txd_queue)


        elif (msg_rxd['msg_type'] == 'IVIM'):
            situation = msg_rxd.get('situation', {})
            if 'situation' in situation:
                situation = situation['situation']
            subtype = situation.get('msg_sub_type')
            if subtype == 'road_works':
                print(f"\n[OBU] Obras detetadas! (Msg ID: {msg_rxd.get('msg_id')})")
                print(" -> AÇÃO: Abrandar veículo.")
                car_move_slower(movement_control_txd_queue)
                print(" -> AÇÃO: Enviar Alarme DENM para outros condutores!")
                
                event_data = {
                    'event_type': 'dangerous_situation',
                    'cause': 'road_works_ahead'
                }
                

                node_id = obd_2_interface['node_id']
                
                den_msg = create_den_message(obd_2_interface, 999, coordinates, event_data)
                den_service_txd_queue.put(den_msg)