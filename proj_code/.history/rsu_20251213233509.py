import socket
import json

HOST = "localhost"
PORT = 5000

print ("=== RSU (Unidade de Estrada) ===")

ALLOWED_ZONES = [
    {"xmin": 0, "xmax": 80, "ymin": 0, "ymax": 80}
]

def is_allowed(x, y, h, m):
    for z in ALLOWED_ZONES:
        if z["xmin"] <= x <= z["xmax"] and z["ymin"] <= y <= z["ymax"] and (1 <= h < 24) and (0 <= m < 60):
            return True
    return False

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
    