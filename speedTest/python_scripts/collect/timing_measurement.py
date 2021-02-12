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
from event_recorder import save_tcp_sample
from estimators.midsummary import get_summaries

PLOT_DISTRIBUTIONS=bool(os.environ.get("PLOT_DISTRIBUTIONS", True)) 

pool = ThreadPool(processes=1)


def record_request(uris, pop_name, pop_machine, pop_ip, times=5000, split_by=4, plot_hist=True, plot_diff=True):
    print(f"Going for pop {pop_name} {pop_machine}")
    result = []
    BACKOFF=60

    NOW = time.time()
    for uri, name in uris:
        print(f"Collectig {name}")
        _, delta, _ = check_version(pop_name, pop_machine, uri, True, None, print_response=True)

        print(f"Potential time {delta}us")

        overall_step_rtts_tcp = []
        overall_step_rtts_tcp_slopes = []
        overall_step_rtts_frame = []
        overall_user_space_deltas = []
        overall_header_times = []

        for _ in range(split_by):
            sniffer = WireSharkSniffer() # in seconds
            future = pool.apply_async(sniffer.capture_packages, args=(SELF_IP, pop_ip))
            time.sleep(2) # give time to tshark to be up

            user_space_deltas = []
            header_times = []
            interval_size = int(times/split_by)
            for n in range(interval_size):
                prob = []
                # backoff
                #time.sleep(0.3)
                retry=True
                finish= False
                while retry:
                    try:
                        r, userspace_delta, header_time  = check_version(pop_name, pop_machine, uri, True, None, timeHeader="Xtime") 
                        printProgressBar(n, interval_size, suffix=f"{n}/{interval_size} {userspace_delta}") 
                        retry=False
                        user_space_deltas.append(userspace_delta)
                        if header_time > -1:
                            header_times.append(header_time)
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

            if len(interactions) != interval_size:
                print(f"WARNING {len(interactions)} collected packages from {interval_size}")

            overall_step_rtts_frame += sniffer.get_rtts_from_frame(interactions)
            rtts_tcp, slopes = sniffer.get_rtts_from_tcp(interactions, pop_ip)
            overall_step_rtts_tcp += rtts_tcp
            overall_step_rtts_tcp_slopes += slopes
            overall_user_space_deltas += user_space_deltas
            overall_header_times += header_times

        print(f"TCP RTT {pop_name} {name} total {len(overall_step_rtts_tcp)} mean:", np.mean(overall_step_rtts_tcp), "variance:", np.var(overall_step_rtts_tcp), "std:", np.std(overall_step_rtts_tcp))
        print(f"USER_SPACE total {len(overall_user_space_deltas)} mean:", np.mean(overall_user_space_deltas), "variance:", np.var(overall_user_space_deltas), "std:", np.std(overall_user_space_deltas))
        print(f"HEADER_TIME  total {len(overall_header_times)} mean:", np.mean(overall_header_times), "variance:", np.var(overall_header_times), "std:", np.std(overall_header_times))

        save_tcp_sample(pop_name, NOW, name, pop_ip, uri, pop_machine, 
            dict(time=NOW, samples=overall_step_rtts_tcp, slopes=overall_step_rtts_tcp_slopes),
            dict(time=NOW, samples=overall_step_rtts_frame),
            dict(time=NOW, samples=overall_user_space_deltas),
            header_times=dict(time=NOW, samples=overall_header_times)
        )

        result.append([overall_step_rtts_frame, overall_step_rtts_tcp, overall_user_space_deltas, overall_header_times])

    if plot_hist:
        
        if plot_diff:
            for i in range(len(uris)):

                rtts_i = result[i][1]
                for j in range(i + 1, len(uris)):
                    rtts_j = result[j][1]

                    mm = min(len(rtts_j), len(rtts_i))
                    rtts_j = rtts_j[:mm]
                    tmp_rtts_i = rtts_i[:mm]

                    label="%s %s"%(uris[i][1], uris[j][1])
                    diff = [tmp_rtts_i[k] - rtts_j[k] for k in range(len(tmp_rtts_i))]
                    
                    summary = get_summaries([diff],w=30)

                    print("Midsummary ", summary, label)
                    plt.hist(diff, bins=len(set(diff)), alpha=0.8, histtype="step", density=True, label=label)


        else:
            for i in range(len(uris)):
                
                rtts = result[i][1]
                user_space=result[i][2]

                summary = get_summaries([rtts],w=30)
                summary_user = get_summaries([user_space],w=30)

                print("Midsummary RTT", summary, "M User", summary_user, uris[i][1])
                plt.hist(rtts, bins=len(set(rtts)), alpha=0.8, histtype="step", density=True, label=uris[i][1])

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
        [

        ("/", "HOME"), 
        ("/sleep10u", "SLEEP_10_MICRO"),
        ("/sleep50u", "SLEEP_50_MICRO"), 
        ("/sleep100u", "SLEEP_100_MICRO"), 
        ("/sleep200u", "SLEEP_200_MICRO"), 
        ("/sleep02", "SLEEP_200_MILLI"), 
        ("/sleep05", "SLEEP_500_MILLI"), 
        ("/sleep1", "SLEEP_1_S"), 
        ("/sleep2", "SLEEP_2_S"), 
        ],
        pop_name, ranges[0]["at"], ranges[0]["ip"], times=100, split_by=1)