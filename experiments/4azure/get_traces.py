import sys
import os
import re
from utils.dbutils import redis_cache

class BreakException(Exception):
    pass

@redis_cache.memoize()
def process(logfiles, start_symbol, pop="CPH"):
    trace = []
    SAVE=False
    FILTER = []
    try:
        for f in logfiles:
            print(f)
            with open(f, "r") as file:
                for line in file:
                    time, log = line.split(": ")
                    values = log.split(",")
                    values = [v.replace("\n", "").strip() for v in values]

                    if len(values) == 4:
                        #print(values[-1])
                        if values[-1] == start_symbol and values[-2] == pop:
                            print(values)
                            if SAVE == True:
                                raise BreakException()
                            SAVE = not SAVE
                            FILTER = [values[0], pop] # testcase and pop
                        if SAVE and values[-2] == FILTER[-1] and values[0] == FILTER[0]:
                            trace.append(values[-1])

                            if len(trace) %100 == 0:
                                sys.stdout.write(f"\r{len(trace)}              ")
    except BreakException:
        pass
    print(len(trace))

if __name__ == "__main__":
    logs = os.listdir(sys.argv[1])
    logs = [f"{sys.argv[1]}/{f}" for f in logs if not f.startswith(".")]
    logs = sorted(logs, key=lambda x: re.sub(r"-\w+\.log$", "", x))
    # sort by date
    process(logs, sys.argv[2])