import subprocess
import re
import sys
import threading

def read_output(process):
    while True:
        line = process.stdout.readline()
        if not line:
            break
        decoded_line = line.decode('utf-8', errors='ignore').strip()
        print(f"STDOUT: {decoded_line}")
        if "serveousercontent.com" in decoded_line:
            # Extract URL
            match = re.search(r'(https://[a-zA-Z0-9-]+\.serveousercontent\.com)', decoded_line)
            if match:
                url = match.group(1)
                with open("url.txt", "w") as f:
                    f.write(url)
                print(f"FOUND URL: {url}")

def start_serveo():
    process = subprocess.Popen(
        ["ssh", "-R", "80:localhost:8000", "serveo.net", "-o", "ServerAliveInterval=60"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    t = threading.Thread(target=read_output, args=(process,))
    t.daemon = True
    t.start()
    
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    start_serveo()
