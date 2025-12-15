import socket
import json
import datetime

RSU_HOST = "localhost"
RSU_PORT = 5000

AU_HOST = "localhost"
AU_PORT = 6000

print("=== OBU (Veículo) ===")

x = float(input("[OBU] X coordinate: "))
y = float(input("[OBU] Y coordinate: "))

while True:
    now = datetime.datetime.now()
    h = int(input("[OBU] Hour: "))
    if (0 <= h < 24) and (h == now.hour):
        break
    print("Invalid hour. Check the current time and enter again.")

while True:
    now = datetime.datetime.now()
    m = int(input("[OBU] Minute: "))
    if (0 <= m < 60) and (m == now.minute):
        break
    print("Invalid minute. Check the current time and enter again.")

msg = {"x": x, "y": y, "h": h, "m": m}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((RSU_HOST, RSU_PORT))
    s.send(json.dumps(msg).encode())

    response = json.loads(s.recv(1024).decode())
    decision = "YES" if response["allowed"] else "NO"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as au:
        au.connect((AU_HOST, AU_PORT))
        au.send(decision.encode())

    if not response["allowed"]:
        event = json.loads(s.recv(1024).decode())
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as au:
            au.connect((AU_HOST, AU_PORT))
            au.send(json.dumps(event).encode())