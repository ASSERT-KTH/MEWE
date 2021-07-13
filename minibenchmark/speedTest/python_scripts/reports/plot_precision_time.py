from common.common import *
from orm.models import *
import matplotlib.pyplot  as plt
from estimators.midsummary import get_summaries
import numpy as np



def plot_scatter_times_for(pop_name):
    cursor = TCPSample.select()
    plt.figure(figsize=(12,12))
    for p in cursor:
        #print(p.get_tcp_samples())
        #print(p.get_header_samples())
        s2 = p.get_header_samples()
        s1 = p.get_tcp_samples()
        m = min(len(s1), len(s2))
        plt.scatter(s2[:m], s1[:m], color="C0", alpha=0.1)
        #break
    
    plt.title(f"POP: {pop_name}")
    plt.show()


def plot_stream(pop_names, test_names):

    fig, axes = plt.subplots(nrows=2,figsize=(23, 23))    
    samples = []
    for name in pop_names:
        for test_name in test_names:
            cursor = TCPSample.select().where(TCPSample.pop_name==name and TCPSample.test_name == test_name).get()


            #for p in cursor:
                #print(p.get_tcp_samples())
                #print(p.get_header_samples())
            s1 = cursor.get_tcp_samples()



                #if diff_home == True:
                    
                #    ptsy.append(s1[0]/1000.0 - d1) # seconds

                #    if use_test_name:
                #        ptsx.append(test_name_2_times[p.test_name])
                #    else:
                #        ptsx.append(s2[0]/1e9 - d2) # 
                #else:
                #    ptsy.append(s1[0]/1000.0) # seconds
                #    if use_test_name:
                #        ptsx.append(test_name_2_times[p.test_name])
                #    else:
                #        ptsx.append(s2[0]/1e9) # 
                #breaks
            axes[1].plot([s for s in s1], 'o', alpha=0.1)
            #samples.append([s for s in s1])
            axes[0].hist([s/1000.0 for s in s1], bins=500, alpha=0.5)

    axes[0].set_xlabel("")
    axes[0].set_ylabel("")

    axes[1].set_xlabel("Sample position")
    axes[1].set_ylabel("TCP cycle ops count")
    #plt.yscale("log")
    #plt.legend()
    plt.show()

def plot_times_for(pop_names, diff_home=True, subplot=-1, w=10, use_test_name=False):

    for name in pop_names:
        cursor = TCPSample.select().where(TCPSample.pop_name==name)
        home = TCPSample.select().where(TCPSample.uri=="/" and TCPSample.pop_name==name).get()


        d1 = get_summaries([home.get_tcp_samples()], w=w)[0]/1000.0
        d2 = get_summaries([home.get_header_samples()], w=w)[0]/1e9

        test_name_2_times = {
            'HOME': dict(order=0, s1 = [], s2=[], time=0),
            "SLEEP_10_MICRO": dict(order=1, s1 = [], s2=[], time=10/1e6),
            "SLEEP_20_MICRO": dict(order=2, s1 = [], s2=[], time=20/1e6),
            "SLEEP_30_MICRO": dict(order=3, s1 = [], s2=[], time=30/1e6),
            "SLEEP_40_MICRO":dict(order=4, s1 = [], s2=[], time=40/1e6) ,
            "SLEEP_50_MICRO": dict(order=5, s1 = [], s2=[], time=50/1e6), 
            "SLEEP_60_MICRO": dict(order=6, s1 = [], s2=[], time=60/1e6), 
            "SLEEP_70_MICRO": dict(order=7, s1 = [], s2=[], time=70/1e6), 
            "SLEEP_80_MICRO": dict(order=8, s1 = [], s2=[], time=80/1e6), 
            "SLEEP_90_MICRO": dict(order=9, s1 = [], s2=[], time=90/1e6), 
            "SLEEP_100_MICRO": dict(order=10, s1 = [], s2=[], time=100/1e6), 
            "SLEEP_200_MICRO": dict(order=11, s1 = [], s2=[], time=200/1e6), 
            "SLEEP_300_MICRO": dict(order=12, s1 = [], s2=[], time=300/1e6), 
            "SLEEP_500_MICRO": dict(order=13, s1 = [], s2=[], time=500/1e6), 
            "SLEEP_875_MICRO": dict(order=14, s1 = [], s2=[], time=875/1e6), 
            "SLEEP_1_MILLI": dict(order=15, s1 = [], s2=[], time=1/1e3), 
            "SLEEP_10_MILLI": dict(order=16, s1 = [], s2=[], time=10/1e3), 
            "SLEEP_20_MILLI": dict(order=17, s1 = [], s2=[], time=20/1e3), 
            "SLEEP_50_MILLI": dict(order=18, s1 = [], s2=[], time=50/1e3), 
            "SLEEP_100_MILLI": dict(order=19, s1 = [], s2=[], time=100/1e3), 
            "SLEEP_200_MILLI": dict(order=20, s1 = [], s2=[], time=200/1e3), 
        }

        # TODO estimate host slope
        ptsx = []
        ptsy = []
        for p in cursor:
            #print(p.get_tcp_samples())
            #print(p.get_header_samples())
            s1 = get_summaries([p.get_tcp_samples()], w=w)
            s2 = get_summaries([p.get_header_samples()], w=w)

            test_name_2_times[p.test_name]['s1'] = s1[0]
            test_name_2_times[p.test_name]['s2'] = s2[0]

            #if diff_home == True:
                
            #    ptsy.append(s1[0]/1000.0 - d1) # seconds

            #    if use_test_name:
            #        ptsx.append(test_name_2_times[p.test_name])
            #    else:
            #        ptsx.append(s2[0]/1e9 - d2) # 
            #else:
            #    ptsy.append(s1[0]/1000.0) # seconds
            #    if use_test_name:
            #        ptsx.append(test_name_2_times[p.test_name])
            #    else:
            #        ptsx.append(s2[0]/1e9) # 
            #break
        all_ = sorted(test_name_2_times.values(), key= lambda x: x["order"])


        if diff_home == True:
            ptsy = [p["s1"]/1000.0 for p in all_]

            if use_test_name:
                ptsx = [p["time"] for p in all_]
            else:
                ptsx = [p["s2"]/1e9 for p in all_]
        else:
            ptsy = [p["s1"]/1000.0 - d1 for p in all_]
            if use_test_name:
                ptsx = [p["time"] for p in all_]
            else:
                ptsx = [p["s2"]/1e9 for p in all_]
            
        plt.plot(ptsx[:subplot], ptsy[:subplot], '--o', label=f"{name}")
    plt.xlabel("Server time (s)")
    plt.ylabel("Client time (s)")
    plt.legend()
    plt.show()

if __name__ == "__main__":

   plot_times_for("bma")