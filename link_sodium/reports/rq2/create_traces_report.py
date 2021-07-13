from neo4j import GraphDatabase
import os
import sys
import json

import matplotlib.pyplot as plt
from utils import *



if __name__ == "__main__":

    latexify(fig_width=4, fig_height=5)

    fig, ax = plt.subplots()

    format_axes(ax, hide=['top', 'right', 'left'], show=["bottom"])
    all_values = []
    i = 1.5
    for alignResult in sys.argv[1:]:
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

    ax.violinplot(all_values, vert=False, widths=0.9, showextrema=False)
    ax.scatter([0]*len(all_values), [1 + x for x in range(len(all_values))], color='red')
    ax.set_xlim(-1)
    #ax.vlines(0,0, len(all_values) + 1, color='C2')
        
    #ax.set_title(fname)
    ax.set_yticks([])
    ax.set_xlabel("DTW value")

    plt.savefig(f"plots/all.pdf")