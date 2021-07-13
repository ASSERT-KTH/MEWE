import grequests
import json
import os
import time
import sys
import functools

pops = json.loads(open(f"{sys.argv[1]}/pops.json", 'r').read())

all_ranges = [
    [(c['at'],p['code'].lower()) for c in json.loads(open(f"{sys.argv[1]}/range_{p['code'].lower()}.json", 'r').read())["valid"]] for p in pops
    if os.path.exists(f"{sys.argv[1]}/range_{p['code'].lower()}.json")
]

all_ranges = functools.reduce(
    lambda x, y: x + y,
    all_ranges
)
#print(all_ranges)

def get_machine(index):
    at, pop = all_ranges[index%len(all_ranges)]
    print(at, pop)
    return f"https://cache-{pop}{at}.hosts.secretcdn.net"

if __name__ == "__main__":


    def cb(response):
        print(response)

    # api-endpoint
    #URL = "https://totally-in-deer.edgecompute.app"
    
    # defining a params dict for the parameters to be sent to the API

    files = os.listdir("test_traces")
    f = []
    index = 0
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            x = eval(open(f"test_traces/{files[i]}", 'r').read())
            y = eval(open(f"test_traces/{files[j]}", 'r').read())

            #print(x, y)
            URL = get_machine(index)
            index += 1
            PARAMS = {'x': x, 'y': y}
    
    # sending get request and saving the response as response object
            f.append(grequests.post(url = URL, data = json.dumps(PARAMS), headers={
                'Host': 'totally-in-deer.edgecompute.app'
            }, timeout=2, verify=False))
            #f.append(grequests.post(url = URL, data = json.dumps(PARAMS)))
    
    now = time.time()
    r = grequests.map(f)
    
    delta = time.time() - now
    for rsp in r:
        try:
            print(rsp.text)
        except:
            pass
    print(f"Time: {delta}s")