from common import *
import os
import json



def print_pop_latex_row(pop_file):
    #print(f"Printing {pop_file}")

    data = json.loads(open(pop_file, "r").read())
    POP = data["pop_name"].upper()
    ns = [d["at"].__str__() for d in data["valid"]]
    range_numbers = ", ".join(ns)
    if PRINT_LATEX:
        print(f"{POP} & {range_numbers} & {len(ns)} \\\\ \\hline")

    return len(ns)

def check_pop(pop_name):
    #print(f"Checking {pop_name}")

    data = json.loads(open(pop_name, "r").read())

    try:
        if len(data["valid"]) == 0 and not PRINT_LATEX:
            print(f"{pop_name} ERROR: not valide machine in the range")
            return False
        
        if data["valid"][-1]["at"] == data["range"][-1]  and not PRINT_LATEX:
            print(f"{pop_name} Maximum range number reached. You should check for a larger range")
            return False
    except Exception as e:
        print(pop_name)
        raise e

    return True
    
    

if __name__ == "__main__":
	
    pop_ranges = [f"{OUT_FOLDER}/{f}" for f in os.listdir(f"{OUT_FOLDER}") if f.startswith("range_")]
    total = 0
    for pop_file in pop_ranges:
        valid = check_pop(pop_file)

        if valid:
            total += print_pop_latex_row(pop_file)