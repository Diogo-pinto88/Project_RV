import subprocess

print("=== Tablet do Condutor ===")
print("1 - Pedir estacionamento")

while True:
    choice = input("> ")
    if choice == "1":
        print("Pedido enviado ao veículo")
        subprocess.run(["python3", "obu.py"])