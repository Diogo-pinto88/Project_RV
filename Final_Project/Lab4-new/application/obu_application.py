#!/usr/bin/env python
# #####################################################################################################
# OBU APPLICATION (PARKING-ONLY PROTOTYPE)
# - Teleop input in separate thread (non-blocking)
# - Parking flow via DEN:
#     p  -> send parking_request
#     receive parking_response -> ask y/n
#     y  -> stop + turn_off + send parking_start
#     1  -> (turn on) send parking_end
#     receive parking_fee / fine_notice -> display
#######################################################################################################

import time
import threading
import Queue as Q

from application.obu_commands import *
import application.app_config as app_conf


# ----------------------------------------------------------------------------------------
# Teleop helpers
# ----------------------------------------------------------------------------------------
def select_option_menu():
    print("+-----------------+-------------------+-------------------------------------------+---------------------+")
    print("|Action           |      Command      |  Effect on Raspberry                      |  vehicle_status     |")
    print("+-----------------+-------------------+-------------------------------------------+---------------------+")
    print("| Open/enter car  |         e         |  Init GPIO pins                           |  opened             |")
    print("| Close/exit car  |         x         |  Cleanup GPIO pins                        |  closed             |")
    print("| Turn on         |         1         |  Set standby GPIO pin                     |  ready              |")
    print("| Turn off        |         0         |  Reset standby GPIO pin                   |  not_ready          |")
    print("| Move forward    |         f         |  Set forward/Reset backward GPIO pin      |  moving             |")
    print("| Move backward   |         b         |  Set backward/Reset forward GPIO pin      |  moving             |")
    print("| Turn right      |         r         |  Set right/Reset left GPIO pin            |  moving or stopped  |")
    print("| Turn left       |         l         |  Set left/Reset right GPIO pin            |  moving or stopped  |")
    print("| Inc speed       |         i         |  Increase duty cycle                      |  moving             |")
    print("| Dec speed       |         d         |  Decrease duty cycle                      |  moving             |")
    print("| Stop            |         s         |  Reset forward and backward GPIO pins     |  stopped            |")
    print("| Park request    |         p         |  Request parking (DEN)                    |  stopped            |")
    print("| Answer yes/no   |       y / n       |  Parking confirmation                     |  -                  |")
    print("+-----------------+-------------------+-------------------------------------------+---------------------+")
    return


def teleop_loop(movement_control_txd_queue, teleop_cmd_queue):
    """
    Runs in a separate thread so input() does not block ITS message handling.
    Sends high-level commands to obu_system through teleop_cmd_queue.
    """
    select_option_menu()
    data = '-'

    while data != 'x':
        try:
            data = input().strip().lower()
        except EOFError:
            data = 'x'

        if data == 'e':
            open_car(movement_control_txd_queue)

        elif data == '1':
            turn_on_car(movement_control_txd_queue)
            teleop_cmd_queue.put({"cmd": "TURN_ON"})

        elif data == '0':
            turn_off_car(movement_control_txd_queue)
            teleop_cmd_queue.put({"cmd": "TURN_OFF"})

        elif data == 'f':
            car_move_forward(movement_control_txd_queue)

        elif data == 'b':
            car_move_backward(movement_control_txd_queue)

        elif data == 'r':
            car_turn_right(movement_control_txd_queue)

        elif data == 'l':
            car_turn_left(movement_control_txd_queue)

        elif data == 'i':
            car_move_faster(movement_control_txd_queue)

        elif data == 'd':
            car_move_slower(movement_control_txd_queue)

        elif data == 's':
            stop_car(movement_control_txd_queue)

        elif data == 'p':
            teleop_cmd_queue.put({"cmd": "PARK_REQUEST"})

        elif data in ['y', 'n']:
            teleop_cmd_queue.put({"cmd": "PARK_CONFIRM", "answer": data})

        elif data == 'x':
            close_car(movement_control_txd_queue)
        
        elif data == 'q':
            break

        else:
            print("Invalid command")
            select_option_menu()

    teleop_cmd_queue.put({"cmd": "TELEOP_EXIT"})


# ----------------------------------------------------------------------------------------
# Thread: application transmission (kept for compatibility with ITS_core)
# ----------------------------------------------------------------------------------------
def obu_application_txd(obd_2_interface, start_flag, my_system_rxd_queue, ca_service_txd_queue, den_service_txd_queue):
    while not start_flag.isSet():
        time.sleep(1)
    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: application_txd - NODE: {}'.format(obd_2_interface["node_id"]), '\n')
    # Parking-only prototype: no periodic tx at application layer
    while True:
        time.sleep(10)


# ----------------------------------------------------------------------------------------
# Thread: application reception (ONLY forward DEN to my_system)
# ----------------------------------------------------------------------------------------
def obu_application_rxd(obd_2_interface, start_flag, services_rxd_queue, my_system_rxd_queue):
    while not start_flag.isSet():
        time.sleep(1)
    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: application_rxd - NODE: {}'.format(obd_2_interface["node_id"]), '\n')

    while True:
        msg_rxd = services_rxd_queue.get()
        if msg_rxd.get('msg_type') == "DEN":
            my_system_rxd_queue.put(msg_rxd)


# ----------------------------------------------------------------------------------------
# Thread: obu_system (parking business logic)
# ----------------------------------------------------------------------------------------
def obu_system(obd_2_interface, start_flag, coordinates, my_system_rxd_queue, movement_control_txd_queue, den_service_txd_queue):

    while not start_flag.isSet():
        time.sleep(1)
    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: my_system - NODE: {}'.format(obd_2_interface["node_id"]), '\n')

    # Start teleop without blocking message handling
    teleop_cmd_queue = Q.Queue()
    teleop_thread = threading.Thread(
        target=teleop_loop,
        args=(movement_control_txd_queue, teleop_cmd_queue),
        daemon=True
    )
    teleop_thread.start()

    if app_conf.debug_sys:
        print("[OBU] Teleop thread started - NODE: {}".format(obd_2_interface['node_id']))

    # Parking state
    parking_request_id = 0

    parking_state = "DRIVING"      # DRIVING | ASKING | PARKED
    pending_req_id = None
    pending_allowed = None
    pending_reason = ""

    park_active = False
    park_req_id_active = None

    while True:

        # -------------------------- handle teleop commands (non-blocking) --------------------------
        try:
            cmd = teleop_cmd_queue.get_nowait()

            if cmd.get("cmd") == "PARK_REQUEST":
                parking_request_id += 1
                pending_req_id = parking_request_id

                den_service_txd_queue.put({
                    "sub_type": "parking_request",
                    "request_id": pending_req_id,
                    "node_id": obd_2_interface.get("node_id"),
                })

                print("\n[OBU] Parking request sent via DEN (request_id={}).".format(pending_req_id))

            elif cmd.get("cmd") == "PARK_CONFIRM":
                if parking_state != "ASKING":
                    continue

                ans = (cmd.get("answer") or "").lower()
                if ans == 'y':
                    turn_off_car(movement_control_txd_queue)

                    den_service_txd_queue.put({
                        "sub_type": "parking_start",
                        "request_id": pending_req_id,
                        "node_id": obd_2_interface.get("node_id"),
                        "allowed_at_request": bool(pending_allowed),
                    })

                    park_active = True
                    park_req_id_active = pending_req_id
                    parking_state = "PARKED"

                    print("[OBU] 🅿️  Parking started (parking_start sent).")

                else:
                    print("[OBU] OK, not parking.")
                    parking_state = "DRIVING"

            elif cmd.get("cmd") == "TURN_ON":
                # If we were parked, end the session
                if park_active:
                    den_service_txd_queue.put({
                        "sub_type": "parking_end",
                        "request_id": park_req_id_active,
                        "node_id": obd_2_interface.get("node_id"),
                    })
                    print("[OBU] ⏱️ parking_end sent. Waiting for fee/fine...")

                    park_active = False
                    park_req_id_active = None
                    parking_state = "DRIVING"

            elif cmd.get("cmd") == "TELEOP_EXIT":
                if app_conf.debug_sys:
                    print("[OBU] Teleop exited (system still running).")

        except Q.Empty:
            pass
        # --------------------------------------------------------------------------------------------

        # -------------------------- handle ITS messages (DEN only) ----------------------------------
        try:
            msg_rxd = my_system_rxd_queue.get(timeout=0.2)
        except Q.Empty:
            continue

        if msg_rxd.get('msg_type') != 'DEN':
            continue

        event = msg_rxd.get("event", {}) or {}
        sub_type = event.get("sub_type") or event.get("subtype")

        # 1) RSU answer to request
        if sub_type == "parking_response":
            pending_allowed = bool(event.get("allowed"))
            pending_reason = event.get("reason", "")
            pending_req_id = event.get("request_id")

            if pending_allowed:
                print("\n[OBU] ✅ You Can Park Here (request_id={}). {}".format(pending_req_id, pending_reason))
            else:
                print("\n[OBU] ❌ You Can't Park Here! You Will Be Fined. (request_id={}). {}".format(pending_req_id, pending_reason))

            print("[OBU] Do You Want To Park Now? (y/n)")
            parking_state = "ASKING"

        # 2) RSU fee
        elif sub_type == "parking_fee":
            amount = event.get("amount", 0.0)
            duration = event.get("duration_s", 0.0)
            req_id = event.get("request_id")
            print("\n[OBU] 🧾 Parking Fee (request_id={}): {:.2f}€ | duration: {:.1f}s".format(
                req_id, float(amount), float(duration)
            ))

        # 3) RSU fine
        elif sub_type == "fine_notice":
            amount = event.get("amount", 0.0)
            duration = event.get("duration_s", 0.0)
            req_id = event.get("request_id")
            reason = event.get("reason", "")
            print("\n[OBU] 🚨 FINED (request_id={}): {:.2f}€ | duration: {:.1f}s | reason: {}".format(
                req_id, float(amount), float(duration), reason
            ))

        else:
            if app_conf.debug_sys:
                print("\n[OBU] DEN received (unhandled subtype): {}".format(event))
        # --------------------------------------------------------------------------------------------
