from common.common import *
from subprocess import Popen, PIPE, check_output, STDOUT
import os

from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import random
import json
import time
from threading import Thread
import urllib3
from event_manager import Publisher, Subscriber
from event_recorder import deploy_subscriber
from collect.get_pops import get_pops

urllib3.disable_warnings()

def deploy_version(number):
    
    if PACKAGE_FOLDER is None:
        raise Exception("PACKAGE_FOLDER env variable not found")
    
    if DEPLOYMENT_SCRIPT is None:
        raise Exception("DEPLOYMENT_SCRIPT env variable not found")
    
    if FASTLY_TOKEN is None:
        raise Exception("FASTLY_TOKEN env variable not found")

    if DEPLOYMENT_SERVICE_ID is None:
        raise Exception("DEPLOYMENT_SERVICE_ID env variable not found")

    os.environ["SERVICE_VERSION"] = number
    os.environ["FASTLY_API_TOKEN"] = FASTLY_TOKEN
    result = check_output(f"bash {DEPLOYMENT_SCRIPT} {DEPLOYMENT_SERVICE_ID}", shell=True, cwd=PACKAGE_FOLDER)


def forever_deploy(publisher, start_at, NOW = 0):
    try:
        while True:

            if time.time() - NOW >= MAX_TIME:
                break

            publisher.publish(EXCHANGE_PROCESS_ID, dict(
                event_type = "DEPLOYMENT_START",
                time = time.time() - NOW
            ))

            deploy_version(f"{start_at}")

            delta = time.time() - NOW

            publisher.publish(EXCHANGE_PROCESS_ID, dict(
                event_type = "DEPLOYMENT_END",
                time = delta
            ))

            time.sleep(DEPLOY_INTERVAL)
            start_at += 1
        print(f"Finishing deployment thread. Ending version {start_at} ")
    except KeyboardInterrupt as e:
        return

def forever_check(publisher, pop_name, ranges, NOW = 0):
    try:
        while True:
            for r in ranges:
                try:

                    if time.time() - NOW >= MAX_TIME:
                        break
                    
                    publisher.publish(EXCHANGE_PROCESS_ID, dict(
                        event_type = "POP_START_CHECK",
                        time = time.time() - NOW,
                        pop = pop_name
                    ))
                
                    body = check_version(pop_name, r)
                    delta = time.time() - NOW

                    publisher.publish(EXCHANGE_PROCESS_ID, dict(
                        event_type = "POP_END_CHECK",
                        time = delta,
                        pop = pop_name,
                        response = body
                    ))
                except Exception as e:
                    print(pop_name, e)
                        
            time.sleep(CHECK_INTERVAL)
        print(f"Finishing checking thread {pop_name} {ranges}")
    except KeyboardInterrupt as e:
        return



if __name__ == "__main__":

    version_start_at = int(time.time())

    # setup publisher
    publisher = Publisher()

    subscriberT = Thread(target=deploy_subscriber)
    subscriberT.start()

    NOW = time.time()

    if LAUNCH_REDEPLOY_THREAD:
        deploy_thread = Thread(target=forever_deploy, args=(publisher, version_start_at, NOW))
        deploy_thread.start()

    time.sleep(DEPLOY_INTERVAL) # Wait for clearance of the first version

    pop_names = get_pops()

    if DYNAMICALLY_LOAD_POP_NAMES:
        from get_pops import get_pops

        pop_names = [d['code'].lower() for d in get_pops()]
        print(f"Loading pop_names dynamically {pop_names}")

    for pop_name in pop_names:
        ranges = [p["code"] for p in get_pop_range(pop_name)]

        if len(ranges) == 0:
            print(f"WARNING no valid machine in pop {pop_name}")
        else:
            if POP_MACHINE_STRATEGY == 0: # random pop machine
                ranges = [random.choice(ranges)]
            print(f"Enabling {pop_name}")
            check_thread = Thread(target=forever_check, args=(publisher,  pop_name, [r["at"] for r in  ranges], NOW))
            check_thread.start()


    deploy_thread.join()
    subscriberT.join()

