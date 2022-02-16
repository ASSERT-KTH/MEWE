import sys
import os
import json
from threading import Thread
import time
import subprocess
import requests
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy import stats
#plt.ion()
fig, axs = plt.subplots(ncols=2)
ax1, ax2 = axs


def plot_events(events, popfilter='ams'):
    
    ax1.cla()
    ax2.cla()

    EVENTS = {
        'PING': [],
        'PINGALL': [],
        'DEPLOY': [],
        'PINGALL': []
    }

    MAP = {
        'PING': 0,
        'PONG': 1
    }

    COLORS = {
        'PING': 'C0',
        'PONG': 'C1'
    }
    # get first time
    MN = None
    PREVIOUS = None
    DELTAS = []
    PINGCONTENTS=[]
    for event in events:
        tokens = event.split(",")
        tokens = [t.strip() for t in tokens]

        action = tokens[0]
        time = tokens[-1]

        if action == "PING":

            time = float(time)
            if MN is None or MN > time:
                MN = time
            result = tokens[2]
            pop = tokens[1]
            if result not in PINGCONTENTS:
                PINGCONTENTS.append(result)
            
            index = PINGCONTENTS.index(result)

            if PREVIOUS is not None:
                if PREVIOUS[0] != index: # version switch
                    # look for nearest DEPLOY event to the left
                    START=PREVIOUS[-1]
                    print( START, float(time))
                    for e in EVENTS['DEPLOY'][::-1]:
                        if e <= PREVIOUS[-1]:
                            START=e
                            break
                    #if PREVIOUS[0] == 0 and MAP[result] == 1: # PING to PONG
                    DELTAS.append(float(time) - START)
            if pop == popfilter:
                EVENTS[action].append((index, float(time)))
                PREVIOUS = EVENTS[action][-1]

        if action == 'DEPLOY':
            
            time = float(time)
            if MN is None or MN > time:
                MN = time

            EVENTS[action].append(float(time))

        if action == 'PINGALL':

            time = float(time)
            if MN is None or MN > time:
                MN = time

            result = tokens[1]

            index = PINGCONTENTS.index(result)
            EVENTS[action].append((index, float(time)))

    print(DELTAS)
    PINGS = [ ev[1] for ev in EVENTS['PING'] if ev[0] == 0 ]
    PONGS = [ ev[1] for ev in EVENTS['PING'] if ev[0] == 1 ]

    PINGSE = [ ev[1] for ev in EVENTS['PINGALL'] if ev[0] == 0 ]
    PONGSE = [ ev[1] for ev in EVENTS['PINGALL'] if ev[0] == 1 ]

    ax2.scatter(PINGS, [10] * len(PINGS), color='C0')
    ax2.scatter(PONGS, [10] * len(PONGS), color='C1')

    #plt.scatter(PINGSE, [2] * len(PINGSE), color='C2')
    #plt.scatter(PONGSE, [2] * len(PONGSE), color='C3')

    ax2.scatter(EVENTS['DEPLOY'], [0] * len(EVENTS['DEPLOY']), color='C1')
    ax1.hist(DELTAS, bins=np.arange(0, 30, 0.5), 
            density=True, alpha=0.3)
    gaussian_kde_zi = stats.gaussian_kde(DELTAS)
    gaussian_kde_zi.covariance_factor = lambda : 0.3
    gaussian_kde_zi._compute_covariance()
    x=np.linspace(0, 30, 500000)
    ax1.plot(x, gaussian_kde_zi(x),  linewidth=1, label='kde', color="C0")
    mean = np.mean(DELTAS)
    ax1.vlines(mean, 0, 1)
    ax1.text(mean, 1, f"{mean:.2f}s")
if __name__ == "__main__":

    pop = sys.argv[2]
    def g(i):

        events_file = sys.argv[1]
        events = open(events_file, 'r').read().split("\n") # one event per line
        plot_events(events, pop)

    ani = FuncAnimation(fig, g, interval=30000)
    plt.show()
    exit(1)

    while True:
        plot_events(events)

        
        fig.canvas.draw()
        fig.canvas.flush_events()
    
        #plt.pause(0.1)
        time.sleep(0.2)
    # plt.show()