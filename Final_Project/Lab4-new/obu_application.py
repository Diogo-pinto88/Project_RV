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
# Thread: application transmission. In this example user triggers CA and DEN messages. 
#		CA message generation requires the sender identification and the inter-generation time.
#		DEN message generarion requires the sender identification, and all the parameters of the event.
#		Note: the sender is needed if you run multiple instances in the same system to allow the 
#             application to identify the intended recipiient of the user message.
#		TIPS: i) You may want to add more data to the messages, by adding more fields to the dictionary
# 			  ii)  user interface is useful to allow the user to control your system execution.
#-----------------------------------------------------------------------------------------
def obu_application_txd(node, node_type, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):

      while not start_flag.isSet():
            time.sleep (1)
      if (app_conf.debug_sys):
            print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(node),'\n')
	
      return



#-----------------------------------------------------------------------------------------
# Thread: application reception. In this example it receives CA and DEN messages. 
# 		Incoming messages are send to the user and my_system thread, where the logic of your system must be executed
# 		CA messages have 1-hop transmission and DEN messages may have multiple hops and validity time
#		Note: current version does not support multihop and time validity. 
#		TIPS: i) if you want to add multihop, you need to change the thread structure and add 
#       		the den_service_txd_queue so that the node can relay the DEN message. 
# 				Do not forget to this also at IST_core.py
#-----------------------------------------------------------------------------------------
def obu_application_rxd(node, node_type, start_flag, services_rxd_queue, my_system_rxd_queue):

      while not start_flag.isSet():
            time.sleep (1)
      if (app_conf.debug_sys):
          print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(node),'\n')
    
	
      while True :
            msg_rxd=services_rxd_queue.get()
            if (msg_rxd['msg_type']=="DEN"):
                  if (app_conf.debug_app_den):
                        print ('obu_application - den messsage received ',msg_rxd)	
                  if msg_rxd['node']!=node:
                        my_system_rxd_queue.put(msg_rxd)



#-----------------------------------------------------------------------------------------
# Thread: my_system - car remote control (test of the functions needed to control your car)
# The car implements a finite state machine. This means that the commands must be executed in the right other.
# Initial state: closed
# closed   - > opened                       opened -> closed | ready:                   ready ->  not_ready | moving   
# not_ready -> stopped | ready| closed      moving -> stopped | not_ready | closed      stopped -> moving not_ready | closed
#-----------------------------------------------------------------------------------------
def obu_system(node, node_type, start_flag, coordinates, obd_2_interface, my_system_rxd_queue, movement_control_txd_queue, den_service_txd_queue):
    
      while not start_flag.isSet():
            time.sleep (1)    
      if (app_conf.debug_sys):
         print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(node),'\n')
     
      # Arranque inicial do carro
      open_car(movement_control_txd_queue)
      turn_on_car(movement_control_txd_queue)
      car_move_forward(movement_control_txd_queue)
      
      while True :
            msg_rxd=my_system_rxd_queue.get()
            
            # --- LÓGICA 1: SEMÁFOROS (Já existia) ---
            # Recebe mensagens DEN ou SPAT do semáforo
            if (msg_rxd['msg_type']=='DEN') or (msg_rxd['msg_type']=='SPAT'):
                  # Verifica se a mensagem não é nossa
                  if (msg_rxd.get('node_type') != node_type):
                        
                        # Extrai o evento (adapta conforme a estrutura da tua mensagem de semáforo)
                        event = msg_rxd.get('event', {})
                        # Se for SPAT a estrutura pode ser diferente, ajusta aqui se necessário:
                        # intersection = msg_rxd.get('intersection', {}) ...

                        if event.get('event_type')=='red_tls':
                              stop_car(movement_control_txd_queue)
                        elif event.get('event_type')=='yellow_tls':      
                              car_move_slower(movement_control_txd_queue)
                        elif event.get('event_type')=='green_tls':
                              car_move_forward(movement_control_txd_queue)

            # --- LÓGICA 2: OBRAS (NOVO - Activity 4) ---
            elif (msg_rxd['msg_type'] == 'IVIM'):
                  situation = msg_rxd.get('situation', {})
                  
                  # Se detetar obras na estrada
                  if situation.get('msg_sub_type') == 'road_works':
                        print(f"\n[OBU {node}] Obras detetadas! A iniciar procedimentos de segurança...")
                        
                        # 1. Abrandar o veículo (Requisito do enunciado)
                        car_move_slower(movement_control_txd_queue)
                        
                        # 2. Emitir Alarme para outros veículos (Requisito do enunciado)
                        print(f"[OBU {node}] A enviar alerta DENM para outros condutores!")
                        
                        event_data = {
                            'event_type': 'dangerous_situation',
                            'cause': 'road_works_ahead'
                        }
                        
                        # Cria a mensagem DENM (Emergency)
                        # coordinates deve ser a localização atual do carro
                        den_msg = create_den_message(node, 999, coordinates, event_data)
                        
                        # Coloca na fila para ser enviada pela antena
                        den_service_txd_queue.put(den_msg)

	