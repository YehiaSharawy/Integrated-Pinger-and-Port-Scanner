# We will need the following module to generate randomized lost packets
import random
from socket import *

serverSocket=socket(AF_INET,SOCK_DGRAM)  # Create a UDP socket, Notice the use of SOCK_DGRAM for UDP packets
serverIP = "127.0.0.1"
serverPort = 9080
serverSocket.bind((serverIP, serverPort))  # Assign IP address and port number to socket
while True:
    message, address = serverSocket.recvfrom(1024)  # Receive the client packet along with the address it is coming from
    print("Client address: ", address)
    message = message.decode().upper()  # Capitalize the message from the client
    rand = random.randint(0, 10)  # Generate random number in the range of 0 to 10
    if rand < 4:  # If rand is less is than 4, we consider the packet lost and do not respond
        continue
    serverSocket.sendto(message.encode(), address)  # Otherwise, the server responds
