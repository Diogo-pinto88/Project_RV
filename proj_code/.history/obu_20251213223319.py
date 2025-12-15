import socket
import json

RSU_HOST = "localhost"
RSU_PORT = 5000

x = float(input("Enter X coordinate: "))
y = float(input("Enter Y coordinate: "))
t = float(input("Enter atual time: "))

message = {"x" : x, "y" : y, "t" : t}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((RSU_HOST, RSU_PORT))
    s.sendall(json.dumps(message).encode('utf-8'))
    response = json.loads(s.recv(1024).decode('utf-8'))

if response["allowed"]:
    print("YES")
else:
    print("NO")
