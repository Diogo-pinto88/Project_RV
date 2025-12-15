import socket
import json
import time
import threading

HOST = "localhost"
PORT = 5000
TOW_TIME = 15 * 60  # 15 minutos

with open("geofencing.json") as f:
    GEOFENCE = json.load(f)["allowed_zones"]

def is_allowed(x, y):
    for z in GEOFENCE:
        if z["xmin"] <= x <= z["xmax"] and z["ymin"] <= y <= z["ymax"]:
            return True
    return False

def tow_timer(vehicle_id, start_time):
    print(f"[RSU] Timer iniciado para {vehicle_id}")
    time.sleep(TOW_TIME)
    print(f"[RSU] 🚨 Reboque acionado para {vehicle_id}")

def handle(conn):
    data = json.loads(conn.recv(1024).decode())
    vehicle_id = data["vehicle_id"]
    x, y = data["position"]
    t = data["time"]

    if is_allowed(x, y):
        response = { "allowed": True }
    else:
        response = { "allowed": False, "reason": "Zona proibida" }
        threading.Thread(
            target=tow_timer,
            args=(vehicle_id, t),
            daemon=True
        ).start()

    conn.send(json.dumps(response).encode())
    conn.close()

with socket.socket() as s:
    s.bind((HOST, PORT))
    s.listen()
    print("[RSU] Antena ativa")
    while True:
        conn, _ = s.accept()
        handle(conn)