import re
import sys
import subprocess

def process(binary):
    # get the textual representation
    wat = subprocess.check_output(
        [
            "wasm2wat",
            binary
        ]
    ).decode()

    # function declaration RE
    FUNCTION_DECLARATION_RE = re.compile(r"[ \t\r]+\(func (.*?) \(type \d+")

    functions = []

    for line in wat.split("\n"):
        m = FUNCTION_DECLARATION_RE.match(line)
        if m:
            print(m.group(1))
            functions.append(m.group(1))


    USAGE = {}
    UNUSED = {}
    for f in functions:
        # check if the function is call at least one time
        try:
            index = wat.index(f"call {f}")
            USAGE[f]  = True
        except Exception as e:
            UNUSED[f]  = True
            pass
    print("Declared functions ", len(functions), "Used", len(USAGE), "Unused", len(UNUSED))
    print(UNUSED.keys())
    #print(wat)

if __name__ == '__main__':
    process(sys.argv[1])