import subprocess

print("=== Tablet do Condutor ===")
print("1 - Pedir estacionamento")

while True:
    choice = input("> ")
    if choice == "1":
        result = subprocess.run(["python3", "obu.py"], capture_output=True, text=True)

        decision = result.stdout.strip()

        if decision == "YES":
            print("Estacionamento permitido.")
        elif decision == "NO":
            print("Estacionamento não permitido.")
        
        