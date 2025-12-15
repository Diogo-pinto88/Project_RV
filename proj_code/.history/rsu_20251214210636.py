import socket
import json
import threading
import time
import datetime

HOST = "localhost"
PORT = 5000

print ("=== RSU (Antena) ===")

ALLOWED_ZONES = [
    {"xmin": 0, "xmax": 80, "ymin": 0, "ymax": 80}
]

def is_allowed(x, y, h, m):
    for z in ALLOWED_ZONES:
        if z["xmin"] <= x <= z["xmax"] and z["ymin"] <= y <= z["ymax"] and (1 <= h < 24) and (0 <= m < 60):
            return True
    return False

def start_countdown(h,m):
    start_time = datetime.datetime.now().replace(hour=h, minute=m, second=0, microsecond=0)
    deadline = start_time + datetime.timedelta(minutes=15)
    print(f"Countdown started at {start_time.time()} . Deadline at {deadline.time().strftime('%H:%M')}")

    while True:
        now = datetime.datetime.now()
        if now >= deadline:
            print("Parking time expired!")
            break
        time.sleep(1)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("RSU is listening...")

    while True:
        conn, _ = s.accept()
        with conn:
            msg = json.loads(conn.recv(1024).decode())
            x, y, h, m = msg["x"], msg["y"], msg["h"], msg["m"]

            allowed = is_allowed(x, y, h, m)

            conn.send(
                json.dumps({"allowed": allowed}).encode()
            )
    