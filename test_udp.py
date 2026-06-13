import socket

target = "192.168.100.106"
port = 50000

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
    print(f"Sending to {target}:{port}")
    s.sendto(b"START_MONITORING", (target, port))
    print("Sent.")
except Exception as e:
    print(e)
