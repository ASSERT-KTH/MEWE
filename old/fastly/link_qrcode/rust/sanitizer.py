import os
from subprocess import check_output
import sys

if __name__ == "__main__":
    bitcodes = os.listdir(sys.argv[1])

    for b in bitcodes:
        if b.endswith(".bc"):
            out = check_output(
                [
                    "llvm-dis",
                    f"{sys.argv[1]}/{b}",
                    "-o",
                    f"{sys.argv[1]}/{b}.ll"
                ]
            )

            content = open(f"{sys.argv[1]}/{b}.ll", "r").read()

            if "triple = \"wasm32" not in content:
                os.remove(f"{sys.argv[1]}/{b}")
                os.remove(f"{sys.argv[1]}/{b}.ll")
