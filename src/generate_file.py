import os

def generate_file(filename, content):
    try:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"File '{filename}' generated successfully.")
    except IOError as e:
        print(f"Failed to generate file '{filename}': {e}")

def generate_random_file(filename, size_in_bytes):
    try:
        generate_file(filename, os.urandom(size_in_bytes).hex())
        print(f"Random file '{filename}' of size {size_in_bytes} bytes generated successfully.")
    except IOError as e:
        print(f"Failed to generate random file '{filename}': {e}")

def generate_pattern_file(filename, pattern, repetitions):
    try:
        #repeat the pattern to create the content, for each line
        content = (pattern + "\n") * repetitions
        generate_file(filename, content)
        print(f"Pattern file '{filename}' generated successfully with pattern '{pattern}' repeated {repetitions} times.")
    except IOError as e:
        print(f"Failed to generate pattern file '{filename}': {e}")

if __name__ == "__main__":
    # generate_pattern_file('test_file.txt', 'Hello World!', 2000)
    generate_random_file('2mb_random_file.bin', 2 * 1024 * 1024)  # 2 MB random file
    generate_random_file('4mb_random_file.bin', 4 * 1024 * 1024)  # 4 MB random file
    generate_random_file('16mb_random_file.bin', 16 * 1024 * 1024)  # 16 MB random file
    generate_random_file('64mb_random_file.bin', 64 * 1024 * 1024)  # 64 MB random file
    generate_random_file('128mb_random_file.bin', 128 * 1024 * 1024)  # 128 MB random file

