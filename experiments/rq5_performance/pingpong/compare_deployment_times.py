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
import itertools
import functools
import matplotlib

import math

fontsize=20
pgf_with_latex = {					  # setup matplotlib to use latex for output
		"pgf.texsystem": "pdflatex",		# change this if using xetex or lautex
		"text.usetex": True,				# use LaTeX to write all text
		"font.family": "serif",
		"font.serif": [],				   # blank entries should cause plots
		"font.monospace": [],
		"axes.labelsize": fontsize,			   # LaTeX default is 10pt font.
		"font.size": fontsize,
		"legend.fontsize": fontsize,			   # Make the legend/label fonts
		"xtick.labelsize": fontsize,			   # a little smaller
		"ytick.labelsize": fontsize,
		"figure.figsize": [30, 30],	 # default fig size of 0.9 textwidth
		#"pgf.preamble": [
		#	r"\\usepackage[utf8x]{inputenc}",	# use utf8 fonts
		#	r"\\usepackage[T1]{fontenc}",		# plots will be generated
		#	r"\\usepackage[detect-all,locale=DE]{siunitx}",
		#	]								   # using this preamble
		}

matplotlib.rcParams.update(pgf_with_latex)

# plt.ion()

APPROX_CURVE=True

def get_events(events, popfilter='ams'):
    
    events = open(events, 'r').read().split("\n")
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
    # get first time
    MN = None
    PREVIOUS = None
    DELTAS = []
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

            if PREVIOUS is not None:
                if PREVIOUS[0] != MAP[result]: # version switch
                    # look for nearest DEPLOY event to the left
                    START=PREVIOUS[-1]
                    #print( START, float(time))
                    for e in EVENTS['DEPLOY'][::-1]:
                        if e <= PREVIOUS[-1]:
                            START=e
                            break
                    #if PREVIOUS[0] == 0 and MAP[result] == 1: # PING to PONG
                    DELTAS.append(float(time) - START)
            if pop == popfilter:
                EVENTS[action].append((MAP[result], float(time)))
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
            EVENTS[action].append((MAP[result], float(time)))

    return DELTAS
    
if __name__ == "__main__":

    events_large = sys.argv[1::3]
    events_small = sys.argv[2::3]
    pops = sys.argv[3::3]
    deltas_large = [get_events(e, pop) for e,pop in zip(events_large, pops)]
    deltas_small = [get_events(e, pop) for e,pop in zip(events_small, pops)]

    tuples = itertools.zip_longest(events_large, events_small, pops, deltas_large, deltas_small)
    tuples = list(tuples)
    fig, axes = plt.subplots(ncols=2, nrows=math.ceil(len(tuples)/2))
    
    axes=[list(ax) for ax in axes]
    print(axes)
    if len(tuples) > 2:
        axes = functools.reduce(lambda x,y: x + y, axes, [])

    for i, ax in enumerate(axes):

        if i >= len(tuples):
            ax.remove()
            break

        event_file_large, event_file_small, popname, deltas_large, deltas_small = tuples[i]
        print(popname)
        ax.set_title(popname)
        ax.set_xlabel("Deployment time (s)")
        ax.set_ylabel("Density")

        ax.hist(deltas_large, density=True, alpha=0.3, label="Multivariant", color='C0')
        ax.hist(deltas_small, density=True, alpha=0.3, label="Original", color="C1")
        
        mean1 = np.mean(deltas_large)
        ax.vlines(mean1, 0, 0.4, color='C0')
        ax.text(mean1+1, 0.4, f"{mean1:.2f}s")

        mean2 = np.mean(deltas_small)
        ax.vlines(mean2, 0, 0.4, color='C1')
        ax.text(mean2-2, 0.4, f"{mean2:.2f}s")
        
        print(len(deltas_large), len(deltas_small))
        if APPROX_CURVE and len(deltas_small) > 0 and len(deltas_large) > 0:
            gaussian_kde_zi = stats.gaussian_kde(deltas_large)
            gaussian_kde_zi.covariance_factor = lambda : 0.3
            gaussian_kde_zi._compute_covariance()
            x=np.linspace(0, 30, 500000)
            ax.plot(x, gaussian_kde_zi(x),  linewidth=2,  color="C0")


            gaussian_kde_zi = stats.gaussian_kde(deltas_small)
            gaussian_kde_zi.covariance_factor = lambda : 0.3
            gaussian_kde_zi._compute_covariance()
            x=np.linspace(0, 30, 500000)
            ax.plot(x, gaussian_kde_zi(x),  linewidth=2, color="C1")

        if i == 0:
            ax.legend()

        '''
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
        '''
    plt.savefig("out/deptimes.pdf", dpi=300)
    #plt.show()    