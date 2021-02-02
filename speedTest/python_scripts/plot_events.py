from common import *
import matplotlib.pyplot as plt
from pymongo import MongoClient

print(MONGO_USER, MONGO_PASS, MONGO_URI)
client = MongoClient(MONGO_URI)
db = client[MONGO_DB]



def plot_events(pop_names=[], filter_out=True, filter_first=True, filter_last=True, draw_interval=True):

    deployments_start = [x["time"] for x in db["deployments"].find() if x["event_type"] == "DEPLOYMENT_START"]    
    deployments_end = [x["time"] for x in db["deployments"].find() if x["event_type"] == "DEPLOYMENT_END"]
    deployments_end = sorted(deployments_end)

    if filter_first:
        deployments_end = deployments_end[1:]
  
    if filter_last:
        deployments_end = deployments_end[:-2]

    print(deployments_end)
    last_deploy_time = deployments_end[-1]  
    TICK_SPACE=10
    #plt.plot(deployments_start, [1]*len(deployments_start), 'o', color='C0')
    plt.yticks([TICK_SPACE + TICK_SPACE*i for i in range(len(pop_names))],pop_names)
    
    for x in deployments_end[1:]:
        plt.vlines(x, ymin=0, ymax=len(pop_names)*TICK_SPACE, alpha=0.1, color="black")

    for i, pop in enumerate(pop_names):
        data = [x for x in db[pop].find() if x["response"] is not None]
        data = sorted(data, key= lambda x: x["time"])
        data_res = [d for d in data if d["response"] is not None]

        if len(data_res) == 0:
            print(f"WARNING {pop} no valid response")
            continue

        last_response = data_res[0]["response"]
        limits = []
        symbols='o^'
        colors=["C2", "C3"]
        buffer = [data_res[0]["time"]]
        count = 0

        y = 10 + i*TICK_SPACE
        deltas = []
        last_switch = 0
        tmp_filter = filter_first
        for d in data_res:
            current_response = d["response"]

            buffer.append(d["time"])

            if last_response != current_response:
                symbol=symbols[count%2]
                c=colors[count%2]


                last_time = buffer[-1]
                previous_deployment_time = -1

                for t in deployments_end[::-1]:
                    if t <= last_time:
                        previous_deployment_time = t
                        break
                if filter_out: # Getting only change time from deployment end
                    buffer = list(filter(lambda x: x >= previous_deployment_time, buffer))

                mx = max(buffer)

                deltas.append([previous_deployment_time, mx])

                if tmp_filter:
                    tmp_filter = False
                    buffer = []
                else:
                    #if filter_last:
                    #    buffer = list(filter(lambda x: x < last_deploy_time, buffer))
                    #if buffer[0] > deployments_end[0]:
                    #    plt.text(buffer[0], y + 2, f"{last_response}", fontsize=8)
                    plt.plot(buffer, [y]*len(buffer), f"{symbol}", color=c, alpha=0.1)

                last_switch = last_time
                count += 1
                buffer = []
            last_response = current_response
                
        
        tmp_filter = filter_first

        deltas = deltas[1:]
        #deltas = deltas[:-2]

        if draw_interval:
            for f, t in deltas[:-1]:
                plt.plot([f, t], [y, y], color='C5')
                plt.text(f, y + 1, f"{t-f:.2f}s")
        print(pop, deltas)
        #plt.plot(check_versions_end, [10 + i*10]*len(check_versions_end), 'o', color='C3') 


    plt.show()



if __name__ == "__main__":

    pop_names = ["bma", "sea", "bog", "osl", "view"]

    if DYNAMICALLY_LOAD_POP_NAMES:
        from get_pops import get_pops

        pop_names = [d['code'].lower() for d in get_pops()]
        print(f"Loading pop_names dynamically {pop_names}")

    plot_events(pop_names, False, False, False, True)