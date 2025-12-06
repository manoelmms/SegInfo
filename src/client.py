# Simple Client to send a file text with objective to compare performance using TLS vs non-TLS (TCP)
import socket
import ssl
import time
import argparse
from datetime import datetime

HOST = 'localhost'
LOG_FILE = 'client_performance.log'
DEBUG = True

def log_performance(data_size, duration, use_tls):
    # Log performance data to a CSV file
    connection_type = 'TLS' if use_tls else 'TCP'
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp},{connection_type},{data_size},{duration:.6f}\n"
    try:
        with open(LOG_FILE, 'a') as log_file:
            log_file.write(log_entry)
    except IOError as e:
        print(f"Failed to write log entry: {e}")

class Client:
    def __init__(self, host, port, use_tls):
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.stats = {'data_size': 0,
                      'transfer_time': 0.0,
                      'average_speed': 0.0,
                      'connection_type': 'TLS' if use_tls else 'TCP',
                      'timestamp': '',}
    
    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.use_tls:
                context = ssl.create_default_context()
                if DEBUG:
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE # Disable certificate verification for debugging to accept self-signed certs
                self.sock = context.wrap_socket(self.sock, server_hostname=self.host)

            self.sock.connect((self.host, self.port))
            print(f"Connected to server {self.host}:{self.port} {'with TLS' if self.use_tls else 'without TLS'}.")
            if self.use_tls:
                print(f"Server certificate:\n{self.sock.getpeercert()}")
                print(f"TLS version: {self.sock.version()}")
                print(f"Cipher: {self.sock.cipher()}")
                print(f"Compression: {self.sock.compression()}")
                print(f"Server hostname: {self.sock.server_hostname}")
                print(f"Socket timeout: {self.sock.gettimeout()}")

        except Exception as e:
            print(f"Failed to connect: {e}")
            self.sock = None

    def send_file(self, file_path):
        if not self.sock:
            print("No connection established.")
            return

        try:
            with open(file_path, 'rb') as file:
                data = file.read()
                data_size = len(data)
                
                # Send file size header
                size_header = data_size.to_bytes(8, byteorder='big')
                self.sock.sendall(size_header)
                
                # Measure only the data transfer time (not ACK reception)
                start_time = time.time()
                self.sock.sendall(data)
                end_time = time.time()
                
                # Wait for acknowledgment (but don't include in timing)
                ack = self.sock.recv(1024)
                
                if ack:
                    ack_decoded = ack.decode('utf-8')
                    print(f"Server acknowledged: {ack_decoded}")
                
                duration = end_time - start_time
                average_speed = data_size / duration if duration > 0 else 0

                # Update stats
                self.stats['data_size'] = data_size
                self.stats['transfer_time'] = duration
                self.stats['average_speed'] = average_speed
                self.stats['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                print(f"Sent {data_size} bytes in {duration:.6f} seconds. Average speed: {average_speed:.2f} bytes/second.")

                # Log performance
                log_performance(data_size, duration, self.use_tls)

        except IOError as e:
            print(f"Failed to read/send file: {e}")
        finally:
            self.sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Send a file to the server with optional TLS.')
    parser.add_argument('file', help='Path to the file to be sent.')
    parser.add_argument('--tls', action='store_true', help='Enable TLS for the client.') # Add argument to enable TLS
    parser.add_argument('--port', type=int, default=65432, help='Port number to connect to the server.')
    args = parser.parse_args()

    client = Client(HOST, args.port, args.tls)
    client.connect()
    client.send_file(args.file)
    print("File transfer completed.")