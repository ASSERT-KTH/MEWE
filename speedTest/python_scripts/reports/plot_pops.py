from common import *
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np
import pandas as pd
import json
import os

def get_pop_size(pop_name):

    print(f"Checking {pop_name}")
    if os.path.exists(f"{OUT_FOLDER}/range_{pop_name}.json"):

        pop_detail = open(f"{OUT_FOLDER}/range_{pop_name}.json", 'r').read()
        pop_detail = json.loads(pop_detail)

        return len(pop_detail["valid"])
    
    return 0

def plot_pops():
    # Make a data frame with the GPS of a few cities:

    pops = open(f"{OUT_FOLDER}/pops.json", 'r').read()
    pops = json.loads(pops)

    lon = [p["coordinates"]["latitude"] for p in pops]
    lats = [p["coordinates"]["longitude"] for p in pops]
    names = [p["code"]for p in pops]
    size = [2.0 * get_pop_size(p["code"].lower()) for p in pops]

    data = pd.DataFrame({
    'lat':lats,
    'lon':lon,
    'name': names,
    'size': size
    })
    
    # A basic map
    m=Basemap(llcrnrlon=-160, llcrnrlat=-75,urcrnrlon=160,urcrnrlat=80)
    m.drawmapboundary(fill_color='#A6CAE0', linewidth=0)
    m.fillcontinents(color='grey', alpha=0.7, lake_color='grey')
    m.drawcoastlines(linewidth=0.1, color="white")
    
    # Add a marker per city of the data frame!
    m.scatter(data['lat'], data['lon'], marker="o", s=size, c="orange", zorder=2, alpha=0.8)

    plt.show()

if __name__ == "__main__":
	plot_pops()
