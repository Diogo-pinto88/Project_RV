import socket
import json
import time

RSU_HOST = "localhost"
RSU_PORT = 5000

VEHICLE_ID = "CAR_1"
POSITION = (80, 20)  # muda para testar

def request_parking():
    msg = {
        "vehicle_id": VEHICLE_ID,
        "position": POSITION,
        "time": time.time()
    }

    with socket.socket() as s:
        s.connect((RSU_HOST, RSU_PORT))
        s.send(json.dumps(msg).encode())
        response = json.loads(s.recv(1024).decode())

    return response

while True:
    cmd = input("[OBU] AU pediu estacionamento? (y/n): ")
    if cmd.lower() == "y":
        res = request_parking()
        if res["allowed"]:
            print("[OBU] ✅ Pode estacionar")
        else:
            print(f"[OBU] ❌ Não pode estacionar ({res['reason']})")