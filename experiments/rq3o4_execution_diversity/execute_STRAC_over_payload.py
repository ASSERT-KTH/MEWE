import os
import sys
import json
from utils.utils import *
import subprocess
import shutil

DIR=os.path.abspath(os.path.dirname(__file__))

if __name__ == "__main__":

    payload_file = sys.argv[1]
    out_folder = sys.argv[2]
    CWD = os.path.abspath(os.path.dirname(payload_file))
    FILENAME = os.path.basename(payload_file)
    
    #CWD = CWD.replace("_", "\_")
    print(CWD, FILENAME)
    command = f"docker run -it --rm -m8g -v {CWD}:/WORKDIR strac {FILENAME}".split(" ")
    p = subprocess.Popen(
        command, 
        stderr=subprocess.STDOUT
    )
    p.wait()
    out, std = p.communicate()

    payload = json.loads(open(payload_file, 'r').read())
    out_file = payload["outputAlignmentMap"]
    shutil.copy(f"{CWD}/out/{out_file}", f"{out_folder}/{out_file}")


