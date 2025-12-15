import socket
import json

HOST = "localhost"
PORT = 6000

print("=== AU (Condutor) ===")
print("À espera da decisão do veículo...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    while True:
        conn, _ = s.accept()
        with conn:
            decision = conn.recv(1024).decode()

            try:
                msg = json.loads(decision)

                # Mensagem de reboque / evento
                if msg.get("event") == "TOW":
                    print(f"{msg.get('message')}")

            except json.JSONDecodeError:
                if decision == "YES":
                    print("Estacionamento permitido")
                else:
                    print("Estacionamento não permitido")
                