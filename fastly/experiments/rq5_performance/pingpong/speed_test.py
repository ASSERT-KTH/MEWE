import sys
import os
import json
from threading import Thread
import time
import subprocess
import requests
import os
import urllib3

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

PING_INTERVAL=0.3 # every 1 second ?
DEPLOY_INTERVAL=30 # every 30 seconds ?

retry_strategy = Retry(
    total=1,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("https://", adapter)
http.mount("http://", adapter)

SERVICE_NAME=os.environ.get("SERVICE_NAME")
urllib3.disable_warnings()

def get_response_from_pop(popname, pc):
    response = http.get(
        f"https://cache-{popname}{pc}.hosts.secretcdn.net",
        headers={
            'Host': SERVICE_NAME
        },
        verify=False,
        timeout=8
    )
    content = response.text
    #print(response.headers)
    #print(content)
    time = response.headers['xtime']
   
    return (content, time)

DIR=os.path.dirname(__file__)
DIR=os.path.abspath(DIR)

def ping_process(WAITFOR, pop):
    startat = time.time()
    cache = open(f"{DIR}/cache.json", 'r').read()
    cache = json.loads(cache)
    while True:
        try:
            #print(f"pinging {pop}")
            
            t = time.time()
            pc = cache[pop]
            r = get_response_from_pop(pop, pc)
            t = time.time()
            f = open("out/speedtest.txt", 'a')
            # ACTION, pop, result, server time, relative time, absolute time
            f.write(f"PING, {pop}, {r[0]}, {r[1]} , {t-startat}, {t}\n")
            f.close()


            #time.sleep(PING_INTERVAL)
            if time.time() - startat >= WAITFOR:
                break
        except KeyboardInterrupt:
            break

def deploy_process(binaries, WAIT_FOR):
    startat = time.time()
    index = 0
    while True:
        try:
            print(f"deploying binary {index}")
            todeploy = binaries[index]
            # fastly compute deploy --verbose --path=$WORKDIR/$PROJECT_NAME.tar.gz --service-id=$SERVICE_ID || exit 1
            out = subprocess.check_output(
                [
                    "fastly",
                    "compute",
                    "deploy",
                    "--path",
                    todeploy,
                    "--service-id",
                    os.environ.get("SERVICE_ID")
                ]
            )
            print(out.decode())
            # write the event and the time
            t = time.time()
            f = open("out/speedtest.txt", 'a')
            f.write(f"DEPLOY, {t}\n")
            f.close()

            time.sleep(DEPLOY_INTERVAL)
            if time.time() - startat >= WAIT_FOR:
                break
            index += 1
            index = index%2
        except KeyboardInterrupt:
            break

if __name__ == "__main__":

    # resetting file
    #f = open("out/speedtest.txt", 'w')
    #f.close()

    ping_binary = sys.argv[1]
    pong_binary = sys.argv[2]

    times = sys.argv[3]
    times = int(times)

    pop = sys.argv[4]
    th1 = Thread(target=ping_process, args=[times,pop])
    th2 = Thread(target=deploy_process, args=([ping_binary, pong_binary], times))

    th1.start()
    th2.start()

    th1.join()
    th2.join()