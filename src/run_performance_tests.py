# File to run performance tests by sending files of various sizes to the server and generating performance graphs
import os
from client import Client
from server import Server
from graph_data import load_performance_data, analyze_performance, create_graph
from generate_server_key import generate_self_signed_cert
import threading
import time


PORT = 65432
TOTAL_TESTS = 5

def start_server(use_tls, port):
    # Start the server in a separate thread
    server_thread = threading.Thread(target=lambda: Server('localhost', port, use_tls).start(), daemon=True)
    server_thread.start()

def run_client(file_path, use_tls, port):
    client = Client('localhost', port, use_tls)
    client.connect()
    client.send_file(file_path)

def generate_test_files():
    from generate_file import generate_random_file
    sizes = [2 * 1024 * 1024, 4 * 1024 * 1024, 8 * 1024 * 1024, 16 * 1024 * 1024, 64 * 1024 * 1024]  # Sizes in bytes
    for size in sizes:
        filename = f"{size // (1024 * 1024)}mb_random_file.bin"
        generate_random_file(filename, size)

def run_performance_tests(use_tls, port):
    test_files = [
        '2mb_random_file.bin',
        '4mb_random_file.bin',
        '8mb_random_file.bin',
        '16mb_random_file.bin',
        '64mb_random_file.bin'
    ]
    # Run clients to send files
    for file in test_files:
        print(f"Sending file: {file}")
        run_client(file, use_tls, port)
        time.sleep(1) 
    
    # Allow time for last server response
    time.sleep(2)

def analyze_performance():
    performance_data = load_performance_data('client_performance.log')
    create_graph(performance_data)
    print("Performance tests completed.")

if __name__ == "__main__":
    if not all(os.path.exists(f"{size}mb_random_file.bin") for size in [2, 4, 8, 16, 64]):
        print("Generating test files...")
        generate_test_files()

    # clean previous log
    if os.path.exists('client_performance.log'):
        os.remove('client_performance.log')

    print("Generating self-signed certificate and key for TLS...")
    generate_self_signed_cert()

    print(f"\n{'='*60}")
    print(f"Starting servers...")
    start_server(use_tls=False, port=PORT)
    start_server(use_tls=True, port=PORT + 1)
    print(f"{'='*60}")
    
    print(f"\n{'='*60}")
    print(f"Running {TOTAL_TESTS} tests...")
    print(f"{'='*60}")
    
    for i in range(TOTAL_TESTS):
        print(f"\n--- TCP Test {i+1}/{TOTAL_TESTS} ---")
        run_performance_tests(use_tls=False, port=PORT)
        print(f"Waiting before next test...")
        time.sleep(3)
    
    print(f"\n{'='*60}")
    print(f"TCP tests completed. Waiting before TLS tests...")
    print(f"{'='*60}")
    time.sleep(5)
    
    for i in range(TOTAL_TESTS):
        print(f"\n--- TLS Test {i+1}/{TOTAL_TESTS} ---")
        run_performance_tests(use_tls=True, port=PORT + 1)
        print(f"Waiting before next test...")
        time.sleep(3)
    
    print(f"\n{'='*60}")
    print("Analyzing performance data...")
    print(f"{'='*60}")
    analyze_performance()

    print("\n All performance tests completed.")