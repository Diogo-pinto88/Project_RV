import socket
import json

HOST = "localhost"
PORT = 5000

ALLOWED_ZONES = [
    {"xmin": 0, "xmax": 50, "ymin": 0, "ymax": 50}
]

def is_allowed(x, y):
    for z in ALLOWED_ZONES:
        if z["xmin"] <= x <= z["xmax"] and z["ymin"] <= y <= z["ymax"]:
            return True
    return False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print("[RSU] RSU ativa")

    while True:
        conn, _ = s.accept()
        with conn:
            msg = json.loads(conn.recv(1024).decode())
            x, y, t = msg["x"], msg["y"], msg["t"]

            allowed = is_allowed(x, y)

            conn.send(
                json.dumps({"allowed": allowed}).encode()
            )
    