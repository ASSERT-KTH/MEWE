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
import datetime
from scipy import stats

PLOT_DISTRIBUTIONS=bool(os.environ.get("PLOT_DISTRIBUTIONS", True)) 

pool = ThreadPool(processes=1)


def record_request(uris, pop_name, pop_machine, pop_ip, times=5000, plot_hist=True, plot_diff=True):
    print(f"Going for pop {pop_name} {pop_machine}")
    result = []
    BACKOFF=60

    NOW = time.time()
    for uri, name in uris:
        print(f"Collectig {name}")
        user_space_deltas = []
        _, delta = check_version(pop_name, pop_machine, "/", True, None)

        print(f"Potential time {delta}us")
        sniffer = WireSharkSniffer(timeout=delta*times*0.000001 + 5) # in seconds
        future = pool.apply_async(sniffer.capture_packages, args=(SELF_IP, pop_ip))
        time.sleep(2) # give time to tshark to be up
        for n in range(times):
            prob = []
            # backoff
            #time.sleep(0.3)
            retry=True
            finish= False
            while retry:
                try:
                    r, userspace_delta  = check_version(pop_name, pop_machine, uri, True, None) 
                    printProgressBar(n, times) 
                    retry=False
                    user_space_deltas.append(userspace_delta)
                except KeyboardInterrupt:
                    finish = True
                    break
                except Exception as e:
                    print(e)
                    print(f"BACKOFF...")
                    time.sleep(BACKOFF)
                    BACKOFF += 10
            if finish:
                break
        time.sleep(2) # give time to dump

        print()
        print("Getting dump")
        
        future.get()
        content = sniffer.stop_and_collect(SELF_IP, pop_ip)
        interactions=sniffer.check_and_filter_events_order(content)

        if len(interactions) != times:
            print(f"WARNING {len(interactions)} collected packages from {times}")

        rtts=sniffer.get_rtts_from_frame(interactions)
        rtts_tcp, slopes =sniffer.get_rtts_from_tcp(interactions, pop_ip)

        print(f"{pop_name} {name} mean:", np.mean(rtts_tcp), "variance:", np.var(rtts_tcp), "std:", np.std(rtts_tcp))


        # Save times in db
        previous = db[f"{pop_name}"].find_one(dict(
            uri=uri,
            test_name=name,
        ))

        if previous:
            previous["user_space"].append(dict(time=NOW, samples=user_space_deltas))
            previous["tcp_rtts"].append(dict(time=NOW, samples=rtts_tcp, slopes=slopes))
            previous["frames_rtts"].append(dict(time=NOW, samples=rtts))
            db[f"{pop_name}"].update_one({'_id': previous["_id"]}, {'$set': previous}, upsert=True)
        else:
            previous = db[f"{pop_name}"].insert_one(dict(
                user_space=[dict(time=NOW, samples=user_space_deltas)], 
                frames_rtts = [dict(time=NOW, samples=rtts)],
                tcp_rtts=[dict(time=NOW, samples=rtts_tcp, slopes=slopes)],
                uri=uri,
                #raw_packages=json.dumps(content),
                test_name=name,
                #interactions=[[json.dumps(sniffer.project_package_info(e)) for e in events] for events in interactions]
            ))

        result.append([rtts, rtts_tcp, user_space_deltas])

    if plot_hist:

        for i in range(len(uris)):
            rtts = result[i][1]
            plt.hist(rtts, bins=len(set(rtts)), alpha=0.2, label=uris[i][1])

        plt.legend()
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
        [("/none", "HOME"),
       # ("/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "REGEX_MATCH30"),
        #("/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "REGEX_MATCH60"),
        ("/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "REGEX_MATCH250")],
        #("/aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "REGEX_MATCH90")], 
        pop_name, ranges[0]["at"], ranges[0]["ip"], times=100)