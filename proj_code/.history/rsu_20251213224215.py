import socket
import json

RSU_HOST = "localhost"
RSU_PORT = 5000

ALLOWED_ZONES = [
    {"x_min": 0, "x_max": 100, "y_min": 0, "y_max": 100} # Just a sample zone
]

def is_allowed(x, y):
    for zone in ALLOWED_ZONES:
        if zone["x_min"] <= x <= zone["x_max"] and zone["y_min"] <= y <= zone["y_max"]:
            return True
    return False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((RSU_HOST, RSU_PORT))
    s.listen()
    print("RSU is listening for incoming connections...")

    while True:
        conn, _ = s.accept()
        with conn:
            msg = json.loads(conn.recv(1024).decode())
            x, y, t = msg["x"], msg["y"], msg["t"]

            response = {"allowed": is_allowed(x, y)}
            conn.send(json.dumps(response).encode())
    