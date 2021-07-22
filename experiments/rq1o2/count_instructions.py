import os
import sys
import re
from utils.utils import *

FUNC_START=re.compile(r"\(func \$")

if __name__ == "__main__":

    fmap  = sys.argv[1]
    fmap, reversed = parse_map(fmap)
    functions = {}
    OVERALL_INSTRUCTIONS = 0
    for w in sys.argv[2:]:
        watfile = w
        content = open(watfile, 'r').read()

        for m in FUNC_START.finditer(content):
            start_at = m.span()[0]


            PARCOUNT = 1
            FUNCTION_CONTENT = ''
            for c in content[start_at + 1:]:
                    if c == '(':
                        PARCOUNT += 1
                    if c == ')':
                        PARCOUNT -= 1
                    
                    if PARCOUNT == 0:
                        break
                    FUNCTION_CONTENT += c
            
            FUNCTION_CONTENT = FUNCTION_CONTENT.split("\n")
            if len(FUNCTION_CONTENT) > 1: # is not a function definition:
                # function names is the first line

                function_name = FUNCTION_CONTENT[0]
                function_name = function_name.split(" ")[1].replace("$", "")
                function_name = re.sub(r"\.\d+", "", function_name)

                if function_name in reversed:
                    print(function_name)
                    if function_name not in functions:
                        functions[function_name] = 1

                        OVERALL_INSTRUCTIONS += len(FUNCTION_CONTENT) - 1
                        sys.stdout.write(f"\r{OVERALL_INSTRUCTIONS}")
                    else:
                        functions[function_name] += 1
    print()
    print(OVERALL_INSTRUCTIONS)
    print(len(functions.keys()))