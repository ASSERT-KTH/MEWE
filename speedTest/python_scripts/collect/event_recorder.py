
from common.common import *
from event_manager import Subscriber
from pymongo import MongoClient
import time

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import json

print(MONGO_USER, MONGO_PASS, MONGO_URI)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

def save_event_in_mongo(data):

    if data["event_type"].startswith("POP_"):
        pop_name = data["pop"]
        time = data["time"]
        response = data["response"] if "response" in data else None

        r = db[pop_name].insert_one(dict(
            pop=pop_name, 
            time = time,
            response = response
        ))
    else:
        r = db["deployments"].insert_one(data)

    if r:
        print(data["pop"] if "pop" in data else "general", data["event_type"], data["time"])
        pass


def deploy_subscriber():
    key = EXCHANGE_PROCESS_ID

    subscriber = Subscriber(1, EXCHANGE_QUEUE, key, 3049, save_event_in_mongo)
    subscriber.setup()


if __name__ == "__main__":

    
    r = db["events"].insert_one(dict(pop_name="test"))
