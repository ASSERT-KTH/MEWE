import os
from requests.packages.urllib3.util.retry import Retry
import json
import requests
from requests.adapters import HTTPAdapter
import time
from subprocess import Popen, PIPE, check_output, STDOUT
import re
from pymongo import MongoClient

FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")
SERVICE_ADDRESS=os.environ.get("SERVICE_ADDRESS", None)	
HIT_TIMEOUT=int(os.environ.get("TIMEOUT", 30))
RES_TIMEOUT=int(os.environ.get("RES_TIMEOUT", 30))
RETRY=int(os.environ.get("RETRY_COUNT", 1))
PRINT_LATEX=bool(os.environ.get("PRINT_LATEX", False))

PACKAGE_FOLDER=os.environ.get("PACKAGE_FOLDER", None)
DEPLOYMENT_SCRIPT=os.environ.get("DEPLOYMENT_SCRIPT", None)
DEPLOYMENT_SERVICE_ID=os.environ.get("DEPLOYMENT_SERVICE_ID", None)

POP_MACHINE_STRATEGY = int(os.environ.get("POP_MACHINE_STRATEGY", 0)) # 0 means random, 1 for all
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 0.1)) # 10ms seconds
DEPLOY_INTERVAL = int(os.environ.get("DEPLOY_INTERVAL", 600)) # 60 seconds, every 1 min
MAX_TIME = int(os.environ.get("MAX_TIME", 3600)) 
DYNAMICALLY_LOAD_POP_NAMES = bool(os.environ.get("DYNAMICALLY_LOAD_POP_NAMES", True)) 
MAX_THREADS_PER_TIME = int(os.environ.get("MAX_THREADS_PER_TIME", 10)) 
LAUNCH_REDEPLOY_THREAD= bool(os.environ.get("LAUNCH_REDEPLOY_THREAD", False))


EXCHANGE=os.environ.get("EXCHANGE", "deploy")
EXCHANGE_HOST=os.environ.get("EXCHANGE_HOST", "127.0.0.1")
EXCHANGE_PORT=os.environ.get("EXCHANGE_PORT", 5672)
EXCHANGE_TYPE=os.environ.get("EXCHANGE_TYPE", "topic")
EXCHANGE_PROCESS_ID=os.environ.get("EXCHANGE_PROCESS_ID", "generate.variant")
EXCHANGE_QUEUE=os.environ.get("EXCHANGE_QUEUE", "timing_test")

CREATE_VIDEO_FROM_EVENTS=bool(os.environ.get("CREATE_VIDEO_FROM_EVENTS", False)) 

SNIFF_INTERFACE=os.environ.get("SNIFF_INTERFACE", "en0")
SELF_IP=os.environ.get("SELF_IP", "127.0.0.1")

REMOVE_DB_AT_FIRST=bool(os.environ.get("REMOVE_DB_AT_FIRST", True)) 

try:
    from common.common_secret import *
except Exception as e:
    print(e)

retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])

def get_pop_range(pop_name):

    if os.path.exists(f"{OUT_FOLDER}/range_{pop_name}.json"):

        pop_detail = open(f"{OUT_FOLDER}/range_{pop_name}.json", 'r').read()
        pop_detail = json.loads(pop_detail)

        return pop_detail["valid"]
    
    return []


def check_version(pop_name, pop_at, uri="", return_full_response=False, sniffer=None, print_response=False, timeHeader=None):

    adapter = HTTPAdapter(max_retries=retries)
    http = requests.Session()
    URI=f"{SERVICE_ADDRESS}"
    try:
        http.mount("https://", adapter)

        if pop_at  % 100  == 0:
            print(f"Hitting {pop_name} at {pop_at}")
        #pops_request = requests.get(, , timeout=HIT_TIMEOUT, max_retries=retries )

        
        result = http.get(f"https://cache-{pop_name}{pop_at}.hosts.secretcdn.net{uri}",headers = {
            "X-Pass": "2",
            "X-Origin": "https_teamc_origin",
            "Host": URI
        },timeout=HIT_TIMEOUT, verify=False)

        delta = result.elapsed.microseconds

        status_code = result.status_code
        response_body = result.content

        if print_response:
            print(response_body)
        
        headers = [(k, v) for k, v in result.headers.items()]

        return_tuple = []

        if return_full_response:
            return_tuple.append(result)
        else:
            return_tuple.append(response_body.decode())

        if timeHeader is not None and timeHeader in result.headers:
            return_tuple.append(int(result.headers[timeHeader]))
        else:
            return_tuple.append(-1)

        return_tuple.append(delta)

        return return_tuple

    except Exception as e:
        raise e

def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=40, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 *
                                                     (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# Call ping and parse the ip ?
def get_ip_from_host(host):
    host = host.replace("https://", "")
    host = host.replace("http://", "")

    out = check_output(f"ping -c 1 {host}".split(" ")).decode()
    pattern = re.compile(r"\d+ bytes from (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")

    match = pattern.search(out)

    
    return match.group("ip")



if REMOVE_DB_AT_FIRST:
    print("REMOVING DB")
    try:
        os.remove(f"{OUT_FOLDER}/fastly4edge.db")
    except:
        pass

    from orm.models import create_db
    create_db()

if __name__ == "__main__":
    print(get_ip_from_host("google.com"))