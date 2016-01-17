import socket

target_host = "0.0.0.0"
target_port = 6464

# Build socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to target
client.connect((target_host,target_port))

# Send data
client.send("GET / HTTP/1.1\r\nHost:google.com\r\n\r\n")

# Receive response
response = client.recv(4096)

print response
