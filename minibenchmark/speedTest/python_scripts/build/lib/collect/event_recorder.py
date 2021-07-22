
from common import *
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

'''

fig, axs = plt.subplots()
axs = [axs]
for i,tpe in enumerate(["-DLARGE_DATASET"]):
	ax = axs[i]
	requests = client["wakoko"]["wasabi_requests"].find(dict(session=f"pure{tpe}"))

	names = []
	pureTimes = []
	wasabiTimes = []
	wakokoTimes = []
	for r in requests:
		names.append(r["name"])

		avgTime = [float(t["time"]) for t in r["data"]]
		avgTime = np.mean(avgTime)

		# find for wasabi one

		wasabi = client["wakoko"]["wasabi_requests"].find(dict(session=f"wasabi{tpe}", name=r["name"]))


		try:
			wasabi = wasabi[0]
		except:
			wasabi = None

		wakoko = client["wakoko"]["wasabi_requests"].find(dict(session=f"wakoko{tpe}", name=r["name"]))

		try:
			wakoko = wakoko[0]
		except:
			wakoko = None

		print(avgTime)
		pureTimes.append(avgTime)


		# logging
		if wakoko:
			try:
				wakokoTimeAvg = [float(t["time"]) for t in wakoko["data"]]
				wakokoTimeAvg = np.mean(wakokoTimeAvg)
				wakokoTimes.append(wakokoTimeAvg)
			except:
				wakokoTimes.append(avgTime)

		else:
			wakokoTimes.append(avgTime)
		if wasabi:
			try:		
				wasabiTimeAvg = [float(t["time"]) for t in wasabi["data"]]

				wasabiTimeAvg = np.mean(wasabiTimeAvg)

				wasabiTimes.append(wasabiTimeAvg)
			except:
				wasabiTimes.append(avgTime)
		else:
			wasabiTimes.append(avgTime)


		

	print(names, len(names))

	assert len(names) == len(pureTimes)


	ax.bar(range(1, 3*len(pureTimes), 3), pureTimes, label="No instrumented" )
	ax.bar(range(0, 3*len(wasabiTimes), 3), wasabiTimes, label="Wasabi instrumentation" )
	ax.bar(range(2, 3*len(wakokoTimes), 3), wakokoTimes, label="WAKOKO instrumentation" )


	ax.set_ylabel('Execution time')
	#ax.set_yscale("log")
	ax.set_title(f'Execution time for PolybenchC {tpe}')
	ax.set_xticks(np.arange(0.3, 3*len(pureTimes), 3))
	ax.set_xticklabels(names, rotation=45)
	ax.legend()

plt.show()

# plt.savefig("plot.png")
'''