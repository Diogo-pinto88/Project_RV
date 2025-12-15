import socket
import json

HOST = "localhost"
PORT = 6000

print("=== AU (Condutor) ===")
print("À espera de mensagens...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, _ = s.accept()
        with conn:
            data = conn.recv(1024).decode()
            try:
                msg = json.loads(data)
                if msg.get("event") == "TOW":
                    print(msg.get("message"))
            except json.JSONDecodeError:
                if data == "YES":
                    print("Estacionamento permitido")
                elif data == "NO":
                    print("Estacionamento não permitido")