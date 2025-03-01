import time
import random
import threading
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.is_alive = True

    def health_check(self):
        # Simulate health check by randomly deciding if server is alive
        self.is_alive = random.choice([True, False])
        logging.info(f'Server {self.address}:{self.port} health check status: {self.is_alive}')

class LoadBalancer:
    def __init__(self):
        self.servers = []
        self.current_index = 0

    def add_server(self, server):
        self.servers.append(server)

    def remove_server(self, server):
        self.servers.remove(server)

    def get_next_server(self):
        if not self.servers:
            logging.warning("No servers available.")
            return None
        
        while True:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            if server.is_alive:
                return server
            else:
                logging.warning(f"Server {server.address}:{server.port} is down, trying next one...")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'OK')
            return
        
        server = load_balancer.get_next_server()
        if not server:
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b'Service Unavailable')
            return

        # Forward the request to the selected server
        logging.info(f'Forwarding request to {server.address}:{server.port}')
        
        time.sleep(0.1)  # Simulate network delay
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f'Response from {server.address}:{server.port}'.encode())

def run_load_balancer_server():
    logging.info('Starting load balancer server...')
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()

def health_check_servers():
    while True:
        logging.info('Performing health checks on servers...')
        for server in load_balancer.servers:
            server.health_check()
        time.sleep(5)

# Create load balancer instance
load_balancer = LoadBalancer()

# Add servers to the load balancer
load_balancer.add_server(Server('192.168.1.1', 80))
load_balancer.add_server(Server('192.168.1.2', 80))
load_balancer.add_server(Server('192.168.1.3', 80))

# Start health checking in a separate thread
health_check_thread = threading.Thread(target=health_check_servers, daemon=True)
health_check_thread.start()

# Start the load balancer server
run_load_balancer_server()