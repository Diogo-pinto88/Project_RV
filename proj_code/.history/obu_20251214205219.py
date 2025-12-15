import socket
import json
import time
import datetime

RSU_HOST = "localhost"
RSU_PORT = 5000  # porta onde a RSU está à escuta

AU_HOST = "localhost"
AU_PORT = 6000   # porta onde o AU está à escuta

print ("=== OBU (Veículo) ===")

# Input do utilizador (OBU)
x = float(input("[OBU] X coordinate: "))
y = float(input("[OBU] Y coordinate: "))

# Caso o input nao seja válido, pedir novamente
while True:
    now = datetime.datetime.now()
    h = int(input("[OBU] Hour: "))
    if (0 <= h < 24) and (h == now.hour):
        break
    print("Invalid hour. Please enter a value between 0 and 23.")

while True:
    now = datetime.datetime.now()
    m = int(input("[OBU] Minute: "))
    if (0 <= m < 60) and (m == now.minute):
        break
    print("Invalid minute. Please enter a value between 0 and 59.")

# Enviar para RSU
msg = {"x": x, "y": y, "h": h, "m": m}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((RSU_HOST, RSU_PORT))
    s.send(json.dumps(msg).encode())
    response = json.loads(s.recv(1024).decode())

decision = "YES" if response["allowed"] else "NO"

# Enviar decisão para o AU
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((AU_HOST, AU_PORT))
    s.send(decision.encode())
