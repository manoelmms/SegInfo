# Simple Server to receive and respond a file text with objective to compare performance using TLS vs non-TLS (TCP)
# The server can handle multiple clients using threading.

import socket
import ssl
import threading
import time
import argparse
import os
from datetime import datetime

BUFFER_SIZE = 4096
HOST = 'localhost'
FILE_SAVE_PATH = 'received_files/'

class Server:
    def __init__(self, host, port, use_tls):
        self.host = host
        self.port = port
        self.use_tls = use_tls
    
    def start(self):
        os.makedirs(FILE_SAVE_PATH, exist_ok=True) # Ensure the directory for saving files exists
        
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5) # Allow up to 5 queued connections

        print(f"Server listening on {self.host}:{self.port} {'with TLS' if self.use_tls else 'without TLS'}")

        context = None
        if self.use_tls:
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile='server.crt', keyfile='server.key')
        try:
            while True:
                conn, addr = server_socket.accept()
                if self.use_tls:
                    conn = context.wrap_socket(conn, server_side=True) # Wrap accepted socket with TLS
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr)) # Handle each client in a new thread
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            server_socket.close()
    
    def handle_client(self, conn, addr):
        print(f"Connection from {addr} has been established.")
        start_time = time.time()
        total_data_received = 0

        data_chunks = []
        try:
            # First, receive the file size (8 bytes)
            size_data = conn.recv(8)
            if len(size_data) < 8:
                print(f"Failed to receive size header from {addr}")
                return
            
            expected_size = int.from_bytes(size_data, byteorder='big')
            print(f"Expecting {expected_size} bytes from {addr}")
            
            # Now receive exactly that many bytes
            while total_data_received < expected_size:
                remaining = expected_size - total_data_received
                chunk_size = min(BUFFER_SIZE, remaining)
                try:
                    data = conn.recv(chunk_size)
                    if not data:
                        break
                    total_data_received += len(data)
                    data_chunks.append(data)
                except (ConnectionResetError, BrokenPipeError, ssl.SSLError) as recv_error:
                    print(f"Error receiving data from {addr}: {recv_error}")
                    break

            data = b''.join(data_chunks)
            end_time = time.time()
            duration = end_time - start_time

            if total_data_received > 0:
                print(f"Received {total_data_received} bytes from {addr} in {duration:.6f} seconds.")
                #timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                #self.save_received_file(data, f"received_from_{addr[0]}_{addr[1]}_{timestamp}.bin")
            
            # Send acknowledgment
            try:
                ack_message = "File received successfully.".encode('utf-8')
                conn.sendall(ack_message)
            except (ConnectionResetError, BrokenPipeError, ssl.SSLError) as send_error:
                print(f"Error sending acknowledgment to {addr}: {send_error}")

            print(f"Connection from {addr} closed. Received {total_data_received} bytes in {duration:.6f} seconds.")
        except Exception as e:
            print(f"Unexpected error from {addr}: {e}")
        finally:
            conn.close()

    def save_received_file(self, data, filename):
        try:
            with open(FILE_SAVE_PATH + filename, 'wb') as file:
                file.write(data)
            print(f"File saved as {FILE_SAVE_PATH + filename}")
        except IOError as e:
            print(f"Failed to save file {filename}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start a simple server with optional TLS.')
    parser.add_argument('--tls', action='store_true', help='Enable TLS for the server.') # Add argument to enable TLS
    parser.add_argument('--port', type=int, default=65432, help='Port number for the server to listen on.')
    args = parser.parse_args()

    server = Server(HOST, args.port, args.tls)
    server.start()
    