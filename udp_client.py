import socket

target_host = "www.youtube.com"
target_port = 80

# Build socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Send data
client.sendto("hi guys =)",(target_host,target_port))

# Receive data
data,addr = client.recvfrom(4096)

print data
