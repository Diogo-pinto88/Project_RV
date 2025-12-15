import socket
import json

RSU_HOST = "localhost"
RSU_PORT = 5000

AU_HOST = "localhost"
AU_PORT = 6000   # porta onde o AU escuta

# Input do utilizador (OBU)
x = float(input("[OBU] Introduz coordenada x: "))
y = float(input("[OBU] Introduz coordenada y: "))
t = float(input("[OBU] Introduz tempo t: "))

# Enviar para RSU
msg = {"x": x, "y": y, "t": t}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((RSU_HOST, RSU_PORT))
    s.send(json.dumps(msg).encode())
    response = json.loads(s.recv(1024).decode())

decision = "YES" if response["allowed"] else "NO"

# Enviar decisão para o AU
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((AU_HOST, AU_PORT))
    s.send(decision.encode())
