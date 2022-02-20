import os
from posix import listdir
import subprocess
import sys
import re
from subprocess import PIPE, check_output, Popen
from multiprocessing import Pool
import shutil
import time

def compile_and_get_results():
    print("Removing old files")
    check_output(
        [
            "rm",
            "-rf",
            "target"
        ]
    )
    check_output(
        [
            "rm",
            "-rf",
            "temp"
        ]
    )
    check_output(
        [
            "rm",
            "-rf",
            "bitcodes"
        ]
    )
    os.mkdir("temp")
    os.mkdir("bitcodes")

    print("Compiling project")
    out = Popen(
        [
            "cargo",
            "build",
            "--target",
            "wasm32-wasi",
            "-v"
        ], stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
        
    )

    stdout, err = out.communicate()
    out.wait()
    err = err.decode()
    err = err.replace("`", "")

    commands = err.split("\n")
    commands = [c.strip() for c in commands]
    commands = [c for c in commands if c.startswith("Running")]
    commands = [c.replace("Running", "") for c in commands]
    commands = [c.strip() for c in commands]


    return commands

CRATE_RE=re.compile(r"--crate-name (.*?) ")
def recompile_to_get_the_bitcode(crate, bash_end):
    CRATE_NAME = CRATE_RE.findall(crate)
    if len(CRATE_NAME) == 0:
        print(crate)
        return

    CRATE_NAME = CRATE_NAME[0]
    print(f"Recompiling crate...{CRATE_NAME}")
    LLVM_FLAGS = "-Clto -C embed-bitcode=yes --emit=llvm-bc -C linker-plugin-lto=no".split(" ")
    

    crate = crate.split(" ")
    index = crate.index("--out-dir")
    if index:
        crate[index + 1] = "temp"
    bash_end.write("\n%s\n"%(" ".join(crate + LLVM_FLAGS), ))
    bash_end.write("\n")
    bash_end.write(f"find temp -name \"{CRATE_NAME}*.bc\" -exec cp {{}} bitcodes/{CRATE_NAME}.bc \;\n")
    
    return

    print()

    try:
        out = check_output(
            crate + LLVM_FLAGS
            #stderr=subprocess.PIPE,
            #stdout=subprocess.PIPE
        )
    except Exception as e:
        print(e)
        return
    #std, err = out.communicate()
    #print(std.decode())
    #print(err.decode())

    now = time.time()
    print("Waiting...")
    #p_status = out.wait()
    #print(f"Lapse {p_status}", time.time() - now)
    retry = 3
    '''
    while p_status != 0:
        print(f"Trying...{retry}")
        time.sleep(2)

        out = Popen(
            crate + LLVM_FLAGS,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
        std, err = out.communicate()
        print(std.decode())
        print(err.decode())

        now = time.time()
        print("Waiting...")
        p_status = out.wait()
        print(f"Lapse {p_status}", time.time() - now)
        retry -=1
        
        if retry == 0:
            return
    # find bc file and copy to the out folder
    '''
    try:
        out =  check_output([
            "find",
            "temp",
            "-name",
            f"{CRATE_NAME}*.bc"
        ]).decode().strip()

        print("Copying:", out)
        if os.path.exists(out):
            
            print("The bitcode file exists")
            if not os.path.exists("bitcodes"):
                os.mkdir("bitcodes")

            shutil.copy(out, f"bitcodes/{CRATE_NAME}.bc")
            # check architecture
            llvmir = check_output(
                [
                    "llvm-dis",
                    f"bitcodes/{CRATE_NAME}.bc",
                    "-o",
                    f"bitcodes/{CRATE_NAME}.ll"
                ]
            )

            llvmcontent = open(f"bitcodes/{CRATE_NAME}.ll", 'r').read()
            if "triple = \"wasm32" not in llvmcontent:
                # remove out or achitecture
                pass
                # os.remove(f"bitcodes/{CRATE_NAME}.bc")
                # os.remove(f"bitcodes/{CRATE_NAME}.ll")

    except Exception as e:
        pass
    print("======================")
def link_all_bitcodes():
    out = check_output(
        [
            os.environ.get("LINKER"),
            *[f"bitcodes/{f}" for f in os.listdir("bitcodes") if f.endswith(".bc")],
            "-o",
            "bitcodes/all.bc"
        ]
    )

    print(out.decode())

if __name__ == "__main__":
    crates = compile_and_get_results()
    get_bitcodes_file = open("get_bitcodes.sh", 'w')
    for crate in crates:
        recompile_to_get_the_bitcode(crate,get_bitcodes_file)
    
    get_bitcodes_file.write("\npython3 sanitizer.py bitcodes\n")
    get_bitcodes_file.write("\n$LINKER $(find bitcodes -name \"*.bc\") -o bitcodes/all.bc")
    get_bitcodes_file.close()


    # link_all_bitcodes()