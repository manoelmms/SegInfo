# File to run performance tests by sending files of various sizes to the server and generating performance graphs
import os
from client import Client
from graph_data import load_performance_data, create_graph
from graph_data import analyze_performance as ap
from generate_server_key import generate_self_signed_cert
import time

PORT = 65432
TOTAL_TESTS = 15

def run_client(file_path, use_tls, port):
    client = Client('localhost', port, use_tls)
    client.connect()
    client.send_file(file_path)

def run_performance_tests(use_tls, port):
    test_file = 'test_file.txt'
    print(f"Sending file: {test_file}")
    run_client(test_file, use_tls, port)
    time.sleep(1)

def analyze_performance():
    performance_data = load_performance_data('client_performance.log')
    ap(performance_data)
    create_graph(performance_data)
    print("Performance tests completed.")

if __name__ == "__main__":
    # Ensure test_file.txt exists
    if not os.path.exists('test_file.txt'):
        from generate_file import generate_pattern_file
        generate_pattern_file('test_file.txt', 'Hello World!', 15)
    
    # clean previous log
    if os.path.exists('client_performance.log'):
        os.remove('client_performance.log')

    print("Generating self-signed certificate and key for TLS...")
    generate_self_signed_cert()

    print(f"\n{'='*60}")
    print(f"Running {TOTAL_TESTS} tests...")
    print(f"{'='*60}")
    
    for i in range(TOTAL_TESTS):
        print(f"\n--- TCP Test {i+1}/{TOTAL_TESTS} ---")
        run_performance_tests(use_tls=False, port=PORT)
        print(f"Waiting before next test...")
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"TCP tests completed. Waiting before TLS tests...")
    print(f"{'='*60}")
    time.sleep(5)
    
    for i in range(TOTAL_TESTS):
        print(f"\n--- TLS Test {i+1}/{TOTAL_TESTS} ---")
        run_performance_tests(use_tls=True, port=PORT + 1)
        print(f"Waiting before next test...")
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print("Analyzing performance data...")
    print(f"{'='*60}")
    analyze_performance()

    print("\n All performance tests completed.")