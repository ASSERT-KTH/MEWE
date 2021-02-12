
from common.common import *
from event_manager import Subscriber
from pymongo import MongoClient
import time

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import json
from orm.models import DeployEvent, TCPSample

def save_event_in_db(data):

    if data["event_type"].startswith("POP_"):

        event = DeployEvent(pop_name=data["pop"], 
        pop_at=-1, time=data["time"], 
        response=data["response"] if "response" in data else "",
        tpe=data["event_type"])

        #pop_name = data["pop"]
        #time = data["time"]
        #response = data["response"] if "response" in data else None

        #r = db[pop_name].insert_one(dict(
        #    pop=pop_name, 
        #    time = time,
        #    response = response
        #))
    else:
        event = DeployEvent(pop_name="DEPLOYMENT", 
        pop_at=-1, time=data["time"], 
        response="",
        tpe=data["event_type"])

        #r = db["deployments"].insert_one(data)

    event.save()


def save_tcp_sample(pop_name, time, test_name, pop_ip, uri, at, tcp_rtts_json, frames_rtts_json, user_space_json, header_times):
    
    # First load the row with the current uri, time, ip, pop_name and test_name
   
    try:
        prexistence = TCPSample.select().where(TCPSample.time == time and TCPSample.test_name == test_name and TCPSample.uri == uri and TCPSample.pop_name == pop_name and TCPSample.pop_ip == pop_ip).get()
        # Update if exist

        if prexistence is not None:
            print(prexistence)

    except Exception as e:

        newSampling = TCPSample(time=time, pop_name=pop_name, test_name=test_name, pop_ip=pop_ip, uri=uri, at=at, tcp_rtts_json=json.dumps(tcp_rtts_json), 
        frames_rtts_json=json.dumps(frames_rtts_json), user_space_json=json.dumps(user_space_json), header_times=header_times)
        newSampling.save()
    # Create otherwise



def deploy_subscriber():
    key = EXCHANGE_PROCESS_ID

    subscriber = Subscriber(1, EXCHANGE_QUEUE, key, 3049, save_event_in_db)
    subscriber.setup()


if __name__ == "__main__":

    
    r = db["events"].insert_one(dict(pop_name="test"))
