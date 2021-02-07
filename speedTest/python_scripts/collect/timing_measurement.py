from common.common import *
import random
import time
import numpy as np
from sniffer_driver import UserSpaceSniffer, WireSharkSniffer
import threading
from pymongo import MongoClient
import os

import urllib3
urllib3.disable_warnings()
from multiprocessing.pool import ThreadPool
import matplotlib.pyplot as plt

PLOT_DISTRIBUTIONS=bool(os.environ.get("PLOT_DISTRIBUTIONS", True)) 

pool = ThreadPool(processes=1)


def record_request(uris, pop_name, pop_machine, pop_ip, times=5000, plot_hist=True, plot_diff=True):

    result = []
    BACKOFF=60
    for uri, name in uris:
        user_space_deltas = []
        _, delta = check_version(pop_name, pop_machine, "/", True, None)
        sniffer = WireSharkSniffer(timeout=delta*times*0.000001 + 5) # in seconds
        future = pool.apply_async(sniffer.capture_packages, args=(SELF_IP, pop_ip))
        time.sleep(2) # give time to tshark to be up
        for n in range(times):
            prob = []
            # backoff
            #time.sleep(0.3)
            retry=True
            while retry:
                try:
                    r, userspace_delta  = check_version(pop_name, pop_machine, uri, True, None) 
                    printProgressBar(n, times) 
                    retry=False
                    user_space_deltas.append(userspace_delta)
                except:
                    time.sleep(BACKOFF)
                    BACKOFF += 10

        time.sleep(2) # give time to dump

    #return
        print("Getting dump")
        content=future.get()
        interactions=sniffer.check_and_filter_events_order(content)

        if len(interactions) != times:
            print(f"WARNING {len(interactions)} collected packages from {times}")

        rtts=sniffer.get_rtts_from_frame(interactions)
        rtts_tcp=sniffer.get_rtts_from_tcp(interactions, pop_ip)

        rtts=[r*1000000 for r in rtts]
        rtts_tcp=[r*1000 for r in rtts_tcp]

        # Save times in db
        print(np.mean(rtts), np.mean(user_space_deltas), np.mean(rtts_tcp))

        r = db[f"{pop_name}"].insert_one(dict(
            user_space=user_space_deltas, 
            frames_rtts = rtts,
            tcp_rtts=rtts_tcp,
            uri=uri,
            #raw_packages=json.dumps(content),
            test_name=name,
            #interactions=json.dumps(interactions)
        ))

        result.append([rtts, rtts_tcp, user_space_deltas])

    if plot_hist:

        rtts1 = result[0][1]
        rtts2 = result[1][1]

        plt.hist(rtts1, bins=len(set(rtts1)), density=True, histtype='step', label=uris[0][1])
        plt.hist(rtts2, bins=len(set(rtts2)), density=True, histtype='step', label=uris[1][1])

        plt.show()

if __name__ == "__main__":

    pop_name="bma"
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
    record_request(
        [("/", "HOME"),
        ("/reallylongkeythatmaytakesometimetoprocessbeacuseisquitelargeandcomplex", "REGEX_MATCH1")], 
        pop_name, ranges[0]["at"], ranges[0]["ip"], times=100)