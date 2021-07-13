import requests
import json
import os
import time
import sys
import functools

if __name__ == "__main__":

    PARAMS = {'x': [0, 1], 'y': [1,2]}
    URL = "https://totally-in-deer.edgecompute.app"
    r = requests.post(url = URL, data = json.dumps(PARAMS))
            #f.append(grequests.post(url = URL, data = json.dumps(PARAMS)))
    
    print(r.text)