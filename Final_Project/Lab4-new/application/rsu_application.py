#!/usr/bin/env python
# #####################################################################################################
# RSU APPLICATION (PARKING-ONLY PROTOTYPE)
# - Receives parking DEN messages: parking_request, parking_start, parking_end
# - Replies with DEN: parking_response, parking_fee, fine_notice
# - No SPAT/TLS, no IVIM
#######################################################################################################

import time
from application.message_handler import *
import application.app_config as app_conf
from application.rsu_commands import *


# -------------------------- PARKING ZONES + HELPERS ------------------------------------
# Priority: forbidden > allowed > default (not allowed)
ALLOWED_ZONES = [
    {"x1": 0, "y1": -60, "x2": 300, "y2": 50},
]
FORBIDDEN_ZONES = [
    {"x1": 0, "y1": -60, "x2": 300, "y2": -200},
]

def _inside_rect(x, y, r):
    try:
        if x is None or y is None:
            return False
        x_min, x_max = sorted([r["x1"], r["x2"]])
        y_min, y_max = sorted([r["y1"], r["y2"]])
        return (x_min <= x <= x_max) and (y_min <= y <= y_max)
    except Exception:
        return False

def check_parking_allowed(x, y):
    for rz in FORBIDDEN_ZONES:
        if _inside_rect(x, y, rz):
            return False, "forbidden_zone"
    for az in ALLOWED_ZONES:
        if _inside_rect(x, y, az):
            return True, "allowed_zone"
    return False, "outside_allowed_zones"
# ---------------------------------------------------------------------------------------


#-----------------------------------------------------------------------------------------
# Thread: rsu application reception (ONLY parking DEN messages)
#-----------------------------------------------------------------------------------------
def rsu_application_rxd(rsu_interface, start_flag, services_rxd_queue, my_system_rxd_queue):
    while not start_flag.isSet():
        time.sleep(1)

    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: rsu_application_rxd - NODE: {}'.format(rsu_interface["node_id"]), '\n')

    while True:
        msg = services_rxd_queue.get()
        if msg.get("msg_type") != "DEN":
            continue

        event = msg.get("event", {}) or {}
        sub = event.get("sub_type") or event.get("subtype")

        # forward only parking messages to rsu_system
        if sub in ["parking_request", "parking_start", "parking_end"]:
            my_system_rxd_queue.put(msg)


#-----------------------------------------------------------------------------------------
# Thread: rsu_system (PARKING ONLY)
#-----------------------------------------------------------------------------------------
def rsu_system(rsu_interface, start_flag, coordinates, my_system_rxd_queue, rsu_control_txd_queue, den_service_txd_queue):

    while not start_flag.isSet():
        time.sleep(1)

    if app_conf.debug_sys:
        print('STATUS: Ready to start - THREAD: rsu_system - NODE: {}'.format(rsu_interface["node_id"]), '\n')

    # init rsu (keep this if your RSU needs to power on for legacy interface)
    start_rsu(rsu_control_txd_queue)
    turn_on(rsu_control_txd_queue)

    node_sub_type = rsu_interface.get("sub_type", "")

    # This prototype is only for parking RSU
    if node_sub_type != "park_entry":
        if app_conf.debug_sys:
            print("[RSU] This RSU is not park_entry. Nothing to do here.")
        while True:
            time.sleep(10)

    if app_conf.debug_sys:
        print("[RSU] Parking mode enabled - NODE: {}".format(rsu_interface['node_id']))

    # sessions by node_id
    parking_sessions = {}  # node_id -> {"start_time":..., "allowed":..., "request_id":..., "reason":...}

    # policy (adjust for demo)
    PRICE_PER_SECOND = 0.01
    FINE_PER_SECOND  = 0.05
    FINE_GRACE_SECONDS = 10.0

    while True:
        msg = my_system_rxd_queue.get()

        if msg.get("msg_type") != "DEN":
            continue

        event = msg.get("event", {}) or {}
        sub = event.get("sub_type") or event.get("subtype")

        node_id = event.get("node_id")
        req_id = event.get("request_id")

        # position attached by DEN service
        x = msg.get("pos_x")
        y = msg.get("pos_y")

        if sub == "parking_request":
            allowed, reason = check_parking_allowed(x, y)

            den_service_txd_queue.put({
                "sub_type": "parking_response",
                "request_id": req_id,
                "node_id": node_id,
                "allowed": allowed,
                "reason": reason
            })

            print("[RSU] parking_response req_id={} node={} at ({},{}) -> allowed={} reason={}".format(
                req_id, node_id, x, y, allowed, reason
            ))

        elif sub == "parking_start":
            # For credibility, re-check zone at start too
            allowed, reason = check_parking_allowed(x, y)

            parking_sessions[node_id] = {
                "start_time": time.time(),
                "allowed": bool(allowed),
                "request_id": req_id,
                "reason": reason
            }

            print("[RSU] parking_start node={} req_id={} allowed={} reason={}".format(
                node_id, req_id, allowed, reason
            ))

        elif sub == "parking_end":
            session = parking_sessions.get(node_id)
            if not session:
                den_service_txd_queue.put({
                    "sub_type": "fine_notice",
                    "request_id": req_id,
                    "node_id": node_id,
                    "duration_s": 0.0,
                    "amount": 0.0,
                    "reason": "no_active_session"
                })
                print("[RSU] parking_end without session node={} req_id={}".format(node_id, req_id))
                continue

            duration = time.time() - session["start_time"]
            allowed = session["allowed"]
            reason = session.get("reason", "")

            if allowed:
                amount = float(duration) * PRICE_PER_SECOND
                den_service_txd_queue.put({
                    "sub_type": "parking_fee",
                    "request_id": session["request_id"],
                    "node_id": node_id,
                    "duration_s": duration,
                    "amount": amount
                })
                print("[RSU] parking_fee node={} req_id={} duration={:.1f}s amount={:.2f}€".format(
                    node_id, session["request_id"], duration, amount
                ))
            else:
                if duration >= FINE_GRACE_SECONDS:
                    amount = float(duration) * FINE_PER_SECOND
                    den_service_txd_queue.put({
                        "sub_type": "fine_notice",
                        "request_id": session["request_id"],
                        "node_id": node_id,
                        "duration_s": duration,
                        "amount": amount,
                        "reason": "illegal_parking_duration:{}".format(reason)
                    })
                    print("[RSU] fine_notice node={} req_id={} duration={:.1f}s amount={:.2f}€ reason={}".format(
                        node_id, session["request_id"], duration, amount, reason
                    ))
                else:
                    den_service_txd_queue.put({
                        "sub_type": "parking_fee",
                        "request_id": session["request_id"],
                        "node_id": node_id,
                        "duration_s": duration,
                        "amount": 0.0
                    })
                    print("[RSU] illegal but within grace node={} duration={:.1f}s (no fine)".format(
                        node_id, duration
                    ))

            # clear session
            try:
                del parking_sessions[node_id]
            except Exception:
                pass
