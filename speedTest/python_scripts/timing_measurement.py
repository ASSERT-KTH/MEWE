from common import *
import random
import time
import numpy as np
from sniffer_driver import UserSpaceSniffer, WireSharkSniffer
import threading


import urllib3
urllib3.disable_warnings()
from multiprocessing.pool import ThreadPool

PLOT_DISTRIBUTIONS=bool(os.environ.get("PLOT_DISTRIBUTIONS", True)) 

pool = ThreadPool(processes=1)

def record_request(uris, pop_name, pop_machine, times=5000, do_diff=True):

    sniffer = WireSharkSniffer()

    BACKOFF=60
    for uri in uris:
        user_space_deltas = []

        future = pool.apply_async(sniffer.capture_packages)
        time.sleep(2) # give time to tshark to be up
        for n in range(times):
            prob = []
            # backoff
            #time.sleep(BACKOFF)
            retry=True
            while retry:
                try:
                    r, userspace_delta  = check_version(pop_name, pop_machine, uri, True, None) # discard delta, we are using package sniffing   
                    printProgressBar(n, times*len(uris)) 
                    retry=False
                    user_space_deltas.append(userspace_delta)
                except:
                    time.sleep(BACKOFF)
                    BACKOFF += 10
        printProgressBar(times*len(uris), times*len(uris))

        time.sleep(2) # give time to dump

    
    #return
        print("Getting dump")
        content=future.get()
    #print(content)
    #print(std.decode())
        print("Filtering packages")
        events=sniffer.filter_packages(content, "192.168.10.168", "157.52.95.25") # Get ip from POP name
    #print(events)
        sniffer.check_and_filter_events_order(events, "192.168.10.168", "157.52.95.25")
        
    #rtts = [r - BACKOFF*1000 for r in rtts]
    print(rtts)

    if len(rtts) != times:
        print(f"WARNING we collected only {len(rtts)} pacakges from {times}")
    if len(rtts) == 0:
        return

    if PLOT_DISTRIBUTIONS:
        import matplotlib.pyplot as plt

        l = len(rtts[0])

        if not do_diff:

            for i in range(l):
                s = [p[i] for p in rtts]
                print(np.mean(s))
                plt.hist(s, bins=len(set(s)), alpha=0.5)
        else:
            if len(uris) != 2:
                raise Exception("DIFF is between two times only")
            
            s = [p[1] - p[0] for p in rtts]
            print(np.mean(s))
            plt.hist(s, bins=len(set(s)), alpha=0.5)
        plt.show()

    print(samples)



if __name__ == "__main__":
    pop_name="bog"
    ranges = get_pop_range(pop_name)

    if len(ranges) == 0:
        print(f"WARNING no valid machine in pop {pop_name}")
    else:
        if POP_MACHINE_STRATEGY == 0: # random pop machine
            ranges = [random.choice(ranges)]
    if len(ranges) == 0:
            print(f"WARNING no valid machine in pop {pop_name}")

    # ""
    #record_request(["/"], pop_name, ranges[0])
    record_request(["/","/reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex"], pop_name, ranges[0])