from common.common import *
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import json
import os
from pymongo import MongoClient
import time
import hashlib

print(MONGO_USER, MONGO_PASS, MONGO_URI)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]

colors = ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'C11']

def get_version_hash(version_str):
    hsh = int(hashlib.sha1(version_str.encode("utf-8")).hexdigest(), 16) % (10 ** 8)

    #print(version_str, hsh%len(colors))
    return colors[hsh%len(colors)]

def draw_events(pop_names=[]):

    overall = [ ]
    for i, pop in enumerate(pop_names):
        data = [x for x in db[pop].find() if x["response"] is not None]
        #data = sorted(data, key= lambda x: x["time"])
        data_res = [d for d in data if d["response"] is not None]


        if len(data_res) == 0:
            print(f"WARNING {pop} no valid response")
            continue

        overall += data_res

    overall = list(sorted(overall, key=lambda x: x["time"]))

    pops = open(f"{OUT_FOLDER}/pops.json", 'r').read()
    pops = json.loads(pops)
    pops = [dict(**p, color='gray') for p in pops]
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, 
                hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.rcParams['axes.facecolor'] = 'black'

    total=len(overall)
    print(total)
    fig = plt.figure()

    SKIP = 1

    for i in range(0, len(overall)): # skip every 10
        event = overall[i]
        print(f"{i}/{total}")

        # process event
        for p in pops:
            if p['code'].lower() == event['pop']:
                p['color'] = get_version_hash(event['response'][10:])

        lon = [p["coordinates"]["latitude"] for p in pops]
        lats = [p["coordinates"]["longitude"] for p in pops]
        names = [p["code"]for p in pops]
        size = [16.0  for p in pops]
        colors = [p["color"] for p in pops]

        data = pd.DataFrame({
            'lat':lats,
            'lon':lon,
            'name': names,
            'size': size,
            'color': colors
        })
        
        if i % SKIP == 0 or i == len(overall) - 1: # Add always last frame
         # A basic map
            fig.clf()
            m=Basemap(llcrnrlon=-160, llcrnrlat=-75,urcrnrlon=160,urcrnrlat=80)
            m.drawmapboundary(fill_color='#FFFFFF', linewidth=0)
            m.fillcontinents(color='gray', alpha=0.7, lake_color='black')
            m.drawcoastlines(linewidth=0.1, color="black")
            
            # Add a marker per city of the data frame!
            m.scatter(data['lat'], data['lon'], marker="o", s=size, c=data['color'], zorder=2, alpha=0.8)
            eventTime = event["time"]
            plt.text(-160,-80, f"T: {eventTime:.2f}s", fontsize=8)
            t = int(time.time())
            plt.savefig(f"{OUT_FOLDER}/video/{t}.png", dpi=400)




if __name__ == "__main__":

    pop_names = ["bma", "sea", "bog", "osl", "view"]

    if DYNAMICALLY_LOAD_POP_NAMES:
        from get_pops import get_pops

        pop_names = [d['code'].lower() for d in get_pops()]
        print(f"Loading pop_names dynamically {pop_names}")

    draw_events(pop_names)