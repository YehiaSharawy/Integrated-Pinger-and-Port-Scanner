from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
from socket import *
import time
import json

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Handle GET requests by serving the file
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open('./templates/PingerAndPortScanner.html', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        self.send_response(200)
        self.end_headers()

        if self.path == '/ping':
            result = pingerModule()
        elif self.path == '/scan':
            result = portScannerModule()

        self.wfile.write(json.dumps({'result': result}).encode())

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def pingerModule():
    serverIP ="127.0.0.1"
    serverPort = 9080
    clientSocket=socket(AF_INET,SOCK_DGRAM) #Creating Client UDP Socket
    rtts=[] #RTTs array to save every RTT and do the statstics
    lost=0 #Accumlator for the lost requests to calculate Loss Rate
    for i in range(1,11): #range(start default=0,end+1,step default=1)
        pingMsg = f"Ping {i} {time.ctime()}" #Message format as Specified, ctime() -> prints current time
        start = time.process_time()  #Start timer before sending ping message to calculate RTT
        clientSocket.sendto(pingMsg.encode(),(serverIP,serverPort))
        try:
            clientSocket.settimeout(1) #Set socket time out to 1 sec, if no operation happened during this period
                #it will raise timeOut exception,it applies to a single call to socket read/write operation.
            serverResponse, serverAddress = clientSocket.recvfrom(1024)
            end = time.process_time()
            rtt = end - start #Calculating RTT
            print(f"Server Responded with {serverResponse.decode()} taking {rtt} seconds")
            rtts.append(rtt)
            clientSocket.settimeout(None) #Removing timeOut as the server already responded
        except timeout:
            lost+=1
            print("Request Timed Out!")
    print(f"\nMinimum RTT: {min(rtts)}")
    print(f"Maximum RTT: {max(rtts)}")
    print(f"Average RTT: {sum(rtts)/len(rtts)}")
    print(f"Packet Loss Rate: {lost/10*100}%") #10 --> # of Packets
    return {
        'message': 'Ping completed.',
        'stats': {
            'min_rtt': min(rtts),
            'max_rtt': max(rtts),
            'avg_rtt': sum(rtts) / len(rtts),
            'packet_loss_rate': lost / 10 * 100
        }
    }

def portScannerModule():
    hostIP = "127.0.0.1"
    open_ports = []
    for port in range(1, 50000):
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(1)  # Set a timeout to avoid blocking indefinitely
        try:
            s.connect((hostIP, port))
            print("Open Connection at Port:", port)
            open_ports.append(port)
        except:
            pass
        finally:
            s.close()

    return {
        'message': 'Port scan completed.',
        'open_ports': open_ports
    }

if __name__ == '__main__':
    server = ThreadedHTTPServer(('127.0.0.1', 9080), RequestHandler)
    print('Server started on port 9080')
    server.serve_forever()