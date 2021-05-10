import re
import sys
import subprocess

def prcess(binary):
    # get the textual representation
    wat = subprocess.check_output(
        [
            "wasm2wat",
            binary
        ]
    )

    print(wat)

if __name__ == '__main__':
    property(sys.argv[1])