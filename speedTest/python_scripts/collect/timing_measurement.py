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

PLOT_DISTRIBUTIONS=bool(os.environ.get("PLOT_DISTRIBUTIONS", True)) 

pool = ThreadPool(processes=1)


def record_request(uris, pop_name, pop_machine, pop_ip, times=5000, do_diff=True):


    BACKOFF=60
    for uri, name in uris:
        user_space_deltas = []
        _, delta = check_version(pop_name, pop_machine, "/", True, None)
        sniffer = WireSharkSniffer(timeout=delta*times*0.000001 + 5) # in seconds
        future = pool.apply_async(sniffer.capture_packages)
        time.sleep(2) # give time to tshark to be up
        for n in range(times):
            prob = []
            # backoff
            #time.sleep(BACKOFF)
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
        print("Filtering packages")
        events=sniffer.filter_packages(content, SELF_IP, pop_ip) # Get ip from POP name
        

        rtts=sniffer.check_and_filter_events_order(events, SELF_IP, pop_ip)

        if len(rtts[0]) != times:
            print(f"WARNING {len(rtts[0])} collected packages from {times}")

        # Save times in db
        print(np.mean(rtts[0]), np.mean(user_space_deltas))

        r = db[f"{pop_name}"].insert_one(dict(
            user_space=user_space_deltas, 
            tcp_rtts = rtts[0],
            uri=uri,
            test_name=name,
            events=events,
            tcp_timestamp = rtts[1]
        ))


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