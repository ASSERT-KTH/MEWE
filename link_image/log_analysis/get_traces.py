import sys
import os


def process(logfiles):
    for f in logfiles:
        print(f)
        with open(f, "r") as file:
            for line in file:
                print(line)

if __name__ == "__main__":
    logs = os.listdir(sys.argv[1])
    logs = [f"{sys.argv[1]}/{f}" for f in logs if not f.startswith(".")]
    # sort by date
    process(logs)