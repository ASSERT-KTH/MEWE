from common import *
from subprocess import Popen, PIPE, check_output, STDOUT
import os

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import random
import json
import time
from threading import Thread
import urllib3
from event_manager import Publisher, Subscriber

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

def check_version(pop_name, pop_at):

    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    try:
        http.mount("https://", adapter)

        if pop_at  % 100  == 0:
            print(f"Hitting {pop_name} at {pop_at}")
        #pops_request = requests.get(, , timeout=HIT_TIMEOUT, max_retries=retries )

        result = http.get(f"https://cache-{pop_name}{pop_at}.hosts.secretcdn.net",headers = {
            "X-Pass": "1",
            "X-Origin": "https_teamc_origin",
            "Host": SERVICE_ADDRESS
        },timeout=HIT_TIMEOUT, verify=False)
        
        status_code = result.status_code
        response_body = result.content

        if status_code != 200:
            raise Exception("Not valid return status")
        
        headers = [(k, v) for k, v in result.headers.items()]

        return response_body.decode()

    except Exception as e:
        raise e

def get_pop_range(pop_name):

    if os.path.exists(f"{OUT_FOLDER}/range_{pop_name}.json"):

        pop_detail = open(f"{OUT_FOLDER}/range_{pop_name}.json", 'r').read()
        pop_detail = json.loads(pop_detail)

        return [p["at"] for p in pop_detail["valid"]]
    
    return []

def forever_deploy(publisher, start_at, mx):
    try:
        while mx > 0:
            publisher.publish(EXCHANGE_PROCESS_ID, dict(
                event_type = "DEPLOYMENT_START",
                time = time.time()
            ))

            deploy_version(f"{start_at}")

            publisher.publish(EXCHANGE_PROCESS_ID, dict(
                event_type = "DEPLOYMENT_END",
                time = time.time()
            ))

            time.sleep(DEPLOY_INTERVAL)
            mx -= 1
            start_at += 1
    except KeyboardInterrupt as e:
        return

def forever_check(publisher, pop_names, mx):
    try:
        while mx > 0:
            for pop_name in pop_names:

                ranges = get_pop_range(pop_name)
                if POP_MACHINE_STRATEGY == 0: # random pop machine
                    ranges = [random.choice(ranges)]

                for r in ranges:
                    publisher.publish(EXCHANGE_PROCESS_ID, dict(
                        event_type = "POP_START_CHECK",
                        time = time.time(),
                        pop = pop_name
                    ))
                    body = check_version(pop_name, r)
                    publisher.publish(EXCHANGE_PROCESS_ID, dict(
                        event_type = "POP_END_CHECK",
                        time = time.time(),
                        pop = pop_name,
                        response = body
                    ))
            time.sleep(CHECK_INTERVAL)
            mx -= 1
    except KeyboardInterrupt as e:
        return


def deploy_subscriber():

    key = EXCHANGE_PROCESS_ID
    subscriber = Subscriber(1, EXCHANGE_QUEUE, key, 3049, lambda x: print(x))
    subscriber.setup()


if __name__ == "__main__":

    version_start_at = 200

    # setup publisher
    publisher = Publisher()

    subscriberT = Thread(target=deploy_subscriber)
    subscriberT.start()

    deploy_thread = Thread(target=forever_deploy, args=(publisher, version_start_at, 10))
    deploy_thread.start()


    check_thread = Thread(target=forever_check, args=(publisher,  ["sea", "bog"], 500))
    check_thread.start()


    deploy_thread.join()
    check_thread.join()
    subscriberT.join()
