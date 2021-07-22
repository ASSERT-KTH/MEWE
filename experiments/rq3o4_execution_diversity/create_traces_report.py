from neo4j import GraphDatabase
import os
import sys
import json
from latexify.common import *

import matplotlib.pyplot as plt


def draw_regular_violinplot():
    latexify(fig_width=4, fig_height=5)

    fig, ax = plt.subplots()

    format_axes(ax, hide=['top', 'right', 'left'], show=["bottom"])
    all_values = []
    i = 1.5
    name = sys.argv[1]
    align_results = sys.argv[2::2]
    preservation = sys.argv[3::2]
    preservation = [ float(p) for p in preservation]
    tuples = zip(align_results, preservation)

    for alignResult, preservation in tuples:
        STRAC_DATA = json.loads(open(alignResult, 'r').read())
        fname = STRAC_DATA["title"]
        fname = fname.replace("_", "\_")
        
        values = []

        for k1, v1 in STRAC_DATA['functionMap'].items():
            for k2, v2 in v1.items():
                values.append(v2)

        ax.text(2, i, fname)
        i += 1

        all_values.append(values)

    

    ax.violinplot(all_values, vert=False, widths=1, showextrema=False)
    #ax.scatter([0]*len(all_values), [1 + x for x in range(len(all_values))], color='red')
    #ax.set_xlim(-1)
    #ax.vlines(0,0, len(all_values) + 1, color='C2')
        
    #ax.set_title(fname)
    ax.set_yticks([])
    ax.set_xlabel("DTW value")

    plt.savefig(f"out/all_traces{name}.pdf")


def draw_histograms():
    latexify(fig_width=4, fig_height=6.5)


    all_values = []
    i = 1.5
    name = sys.argv[1]
    align_results = sys.argv[2::2]
    preservation = sys.argv[3::2]
    preservation = [ float(p) for p in preservation]
    tuples = zip(align_results, preservation)
    tuples = list(tuples)
    fig, axs = plt.subplots(nrows=len(tuples), sharex=False)

    for i, ax in enumerate(axs):
        print(i)
        alignResult, preservation = tuples[i]


        #if i != len(tuples) - 1:
        #    format_axes(ax, hide=['top', 'right', 'left', "bottom"])
        #    ax.set_yticks([])
        #    ax.set_xticks([])
        #else:
        format_axes(ax, hide=['top', 'right'], show=[ "bottom", 'left'])

        STRAC_DATA = json.loads(open(alignResult, 'r').read())
        fname = STRAC_DATA["title"]
        fname = fname.replace("_", "\_")
        
        values = []

        for k1, v1 in STRAC_DATA['functionMap'].items():
            for k2, v2 in v1.items():
                values.append(v2)

        #ax.text(2, i, fname)
        i += 1
        ax.hist(values, cumulative=True, histtype="step", density=True)
        ax.set_xlim(0)
        ax.set_title(fname)
        all_values.append(values)

    

    #ax.violinplot(all_values, vert=False, widths=1, showextrema=False)
    #ax.scatter([0]*len(all_values), [1 + x for x in range(len(all_values))], color='red')
    #ax.set_xlim(-1)
    #ax.vlines(0,0, len(all_values) + 1, color='C2')
        
    #ax.set_title(fname)
    #ax.set_yticks([])
    #ax.set_xlabel("DTW value")

    plt.tight_layout()
    plt.savefig(f"out/all_traces{name}.pdf")

if __name__ == "__main__":

    # draw_regular_violinplot()
    draw_histograms()