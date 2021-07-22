import os
import sys
import subprocess
import time

def analyze(bin, times):
    name = os.path.basename(bin)
    name, ext = os.path.splitext(name)

    while True:
        try:
            print("Compiling...")
            t1 = time.time()
            out = subprocess.check_output([
                os.environ.get("WASMTIME"),
                "wasm2obj",
                bin,
                "out/t.obj",
                '--opt-level',
                "2"
            ])
            t2 = time.time()
            print(out.decode())
            f = open(f"out/{name}.times.txt", "a")
            f.write(f"{t2 - t1}\n")
            f.close()
        except KeyboardInterrupt:
            break

if __name__ == "__main__":

    # resetting file
    #f = open("out/speedtest.txt", 'w')
    #f.close()

    ping_binary = sys.argv[1]
    times = sys.argv[2]
    times = int(times)

    analyze(ping_binary, times)