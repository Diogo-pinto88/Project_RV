import socket

HOST = "localhost"
PORT = 6000

print("=== AU (Condutor) ===")
print("À espera da decisão do veículo...")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()

    conn, _ = s.accept()
    with conn:
        decision = conn.recv(1024).decode()

        if decision == "YES":
            print("Estacionamento permitido")
        else:
            print("Estacionamento não permitido")
        