#!/usr/bin/env python
from socket import *
import sys, time
from threading import Thread, Event
from Queue import *

# Link layer
from data_link.multicast import *

# Transport & network
from transport_network.geonetworking import *

# Facilities (CA + DEN)
from facilities.common_services import *

# Application (OBU + RSU)
from application.obu_application import *
from application.rsu_application import *

# In-vehicle (movement + location)
from in_vehicle_network.car_control import *

# RSU control (can keep; harmless even if park_entry)
from rsu_legacy_systems.rsu_control import *

# Physical map / options
import ITS_maps as maps
import ITS_options as its_conf


# --------------------------------------------------------------------------------------
# QUEUES (minimal set for CA + DEN prototype)
# --------------------------------------------------------------------------------------
my_system_rxd_queue = Queue()
movement_control_txd_queue = Queue()
rsu_control_txd_queue = Queue()

ca_service_txd_queue = Queue()
den_service_txd_queue = Queue()

services_rxd_queue = Queue()

geonetwork_txd_queue = Queue()
geonetwork_rxd_ca_queue = Queue()
geonetwork_rxd_den_queue = Queue()

multicast_txd_queue = Queue()
multicast_rxd_queue = Queue()

# optional beacon queue (multicast_rxd expects it)
beacon_rxd_queue = Queue()

# EVENTS
start_flag = Event()

# SHARED VARIABLES
coordinates = dict()
node_interface = dict()


# --------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------
def main(argv):
    global node_interface, coordinates

    if (len(argv) < 2):
        print('ERROR: Missing arguments: node_id')
        sys.exit()

    node_id = argv[1]
    visual = False
    current_time = repr(time.time())

    if node_id not in maps.map:
        print("ERROR: node_id {} not found in ITS_maps".format(node_id))
        sys.exit()

    coordinates = {'x': maps.map[node_id]['x'], 'y': maps.map[node_id]['y'], 't': current_time}
    node_type = maps.map[node_id]['type']
    node_sub_type = maps.map[node_id]['sub_type']

    # plus_info safe
    if (node_sub_type == 'car') or (node_sub_type == 'tls'):
        plus_info = ''
    else:
        plus_info = maps.map[node_id].get('plus_info', '')

    maps.map[node_id]['status'] = 'ready'

    # Build node_interface (OBU vs RSU)
    if node_type == maps.obu_node:
        speed = maps.map[node_id]['speed']
        direction = maps.map[node_id]['direction']
        heading = maps.map[node_id]['heading']
        node_interface = {
            'node_id': node_id,
            'type': node_type,
            'sub_type': node_sub_type,
            'speed': speed,
            'direction': direction,
            'heading': heading,
            'plus_info': plus_info,
            'time': current_time
        }

    elif node_type == maps.rsu_node:
        # Parking RSU (park_entry) minimal interface
        node_interface = {
            'node_id': node_id,
            'type': node_type,
            'sub_type': node_sub_type,
            'plus_info': plus_info,
            'time': current_time
        }

    else:
        print("ERROR: Prototype supports only OBU + RSU.")
        sys.exit()

    threads = []

    try:
        # --------------------------------------------------------------------------------------
        # APPLICATION LAYER THREADS
        # --------------------------------------------------------------------------------------
        if node_type == maps.obu_node:
            t = Thread(target=obu_application_txd,
                       args=(node_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue,))
            t.start(); threads.append(t)

            t = Thread(target=obu_application_rxd,
                       args=(node_interface, start_flag, services_rxd_queue, my_system_rxd_queue,))
            t.start(); threads.append(t)

            t = Thread(target=obu_system,
                       args=(node_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue, den_service_txd_queue,))
            t.start(); threads.append(t)

        if node_type == maps.rsu_node:
            # We do NOT start rsu_application_txd (TLS/SPAT/IVIM removed for prototype)
            t = Thread(target=rsu_application_rxd,
                       args=(node_interface, start_flag, services_rxd_queue, my_system_rxd_queue,))
            t.start(); threads.append(t)

            t = Thread(target=rsu_system,
                       args=(node_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue, den_service_txd_queue,))
            t.start(); threads.append(t)

        # --------------------------------------------------------------------------------------
        # FACILITIES LAYER THREADS (CA + DEN)
        # --------------------------------------------------------------------------------------
        t = Thread(target=ca_service_txd,
                   args=(node_interface, start_flag, coordinates, ca_service_txd_queue, geonetwork_txd_queue,))
        t.start(); threads.append(t)

        t = Thread(target=ca_service_rxd,
                   args=(node_interface, start_flag, geonetwork_rxd_ca_queue, services_rxd_queue,))
        t.start(); threads.append(t)

        t = Thread(target=den_service_txd,
                   args=(node_interface, start_flag, coordinates, den_service_txd_queue, geonetwork_txd_queue,))
        t.start(); threads.append(t)

        t = Thread(target=den_service_rxd,
                   args=(node_interface, start_flag, geonetwork_rxd_den_queue, services_rxd_queue, geonetwork_txd_queue,))
        t.start(); threads.append(t)

        # --------------------------------------------------------------------------------------
        # TRANSPORT & NETWORK THREADS
        # --------------------------------------------------------------------------------------
        t = Thread(target=geonetwork_txd,
                   args=(node_interface, start_flag, geonetwork_txd_queue, multicast_txd_queue,))
        t.start(); threads.append(t)

        # geonetwork_rxd expects CA, DEN, SPAT, IVIM queues.
        dummy_spat_queue = Queue()
        dummy_ivim_queue = Queue()

        t = Thread(target=geonetwork_rxd,
                   args=(node_interface, start_flag, multicast_rxd_queue,
                         geonetwork_rxd_ca_queue, geonetwork_rxd_den_queue,
                         dummy_spat_queue, dummy_ivim_queue,))
        t.start(); threads.append(t)

        # --------------------------------------------------------------------------------------
        # LINK LAYER THREADS
        # --------------------------------------------------------------------------------------
        t = Thread(target=multicast_rxd,
                   args=(node_interface, start_flag, coordinates, multicast_rxd_queue, beacon_rxd_queue,))
        t.start(); threads.append(t)

        t = Thread(target=multicast_txd,
                   args=(node_interface, start_flag, multicast_txd_queue,))
        t.start(); threads.append(t)

        # --------------------------------------------------------------------------------------
        # IN-VEHICLE THREADS (only for OBU)
        # --------------------------------------------------------------------------------------
        if node_type == maps.obu_node:
            t = Thread(target=update_location,
                       args=(node_interface, start_flag, coordinates, visual,))
            t.start(); threads.append(t)

            t = Thread(target=movement_control,
                       args=(node_interface, start_flag, coordinates, movement_control_txd_queue,))
            t.start(); threads.append(t)
        else:
            # optional - can keep
            t = Thread(target=rsu_control,
                       args=(node_interface, start_flag, coordinates, rsu_control_txd_queue,))
            t.start(); threads.append(t)

        # --------------------------------------------------------------------------------------
        # IMPORTANT: kickstart CA generation time (your ca_service_txd blocks on .get())
        # --------------------------------------------------------------------------------------
        if ca_service_txd_queue.empty():
            ca_service_txd_queue.put(1.0)  # 1 Hz CAMs (change to 0.5 for 2 Hz)

        # GO
        start_flag.set()

    except:
        print('STATUS: Error opening one of the threads -  NODE: {}'.format(node_id), '\n')
        for t in threads:
            t.join()
        sys.exit()

    return


if __name__ == "__main__":
    main(sys.argv[0:])
