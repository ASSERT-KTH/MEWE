from neo4j import GraphDatabase
import os
import sys
import json
from latexify.common import *

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from matplotlib import cm, colors
import math
import random

_3D=True
PLOT_COLISSION_PER_PLOT_3D=False

FONTSIZE=20
def draw_histograms():
    latexify(fig_width=10, fig_height=15, tick_size=FONTSIZE, font_size=FONTSIZE)

    markers = [
        '.',
        'o',
        'v',
        'x',
        '+',
        '*',
        's',
        '1'
    ]
    all_values = []
    i = 1.5
    #name = sys.argv[1]
    align_results = sys.argv[1::2]
    names = sys.argv[2::2]
    tuples = zip(align_results, names)
    tuples = list(tuples)
    fig, ax = plt.subplots()

    colormap = plt.cm.viridis# LinearSegmentedColormap
    Ncolors = min(colormap.N,len(tuples))
    mapcolors = [colormap(int(x*colormap.N/Ncolors)) for x in range(Ncolors)]

    for i, t in enumerate(tuples):
        print(i)
        hashes, name = tuples[i]


        #if i != len(tuples) - 1:
        #    format_axes(ax, hide=['top', 'right', 'left', "bottom"])
        #    ax.set_yticks([])
        #    ax.set_xticks([])
        #else:
        format_axes(ax, hide=['top', 'right'], show=[ "bottom", 'left'])

        hashes_DATA = json.loads(open(hashes, 'r').read())
        fname = hashes_DATA["endpoint"] if "endpoint" in hashes_DATA else name
        fname = fname.replace("_", "\_")

        values = [
            (p, hashes_DATA[p]["ratio"]) for p in hashes_DATA.keys() if
            p != "endpoint"
        ]

        values = sorted(values, key=lambda x: x[0])
        ax.plot(
            range(len(values)),
            [x[1] for x in values],
            f'{markers[i]}',
            color=mapcolors[i],
            alpha=0.3,
            label=f"{name}".replace("_", "\_")
        )
        #ax.set_xlim(0, 1)
        #ax.set_yticklabels([x[0] for x in values])
        #ax.set_yticks(range(len(values)))
        
        print(values)

    ax.legend(bbox_to_anchor = (0.5, 1))
    ax.set_xlabel("Edge node")
    ax.set_ylabel("Uniqueness ratio")
    ax.set_yticks([0, 0.5, 1.0])
    plt.tight_layout()
    plt.savefig(f"out/hashes_collision.pops.pdf")

def get_values(f):
    hashes_DATA = json.loads(open(f, 'r').read())
    fname = hashes_DATA["endpoint"] if "endpoint" in hashes_DATA else name
    fname = fname.replace("_", "\_")

    values = [
        (p, hashes_DATA[p]["ratio"]) for p in hashes_DATA.keys() if
        p != "endpoint"
    ]

    return values

FONT_SIZE_LABEL=100
FONT_SIZE_TICKS=100
LABEL_PAD=250

def draw_3d():
    latexify(fig_width=10, fig_height=10)


    all_values = []
    i = 1.5
    #name = sys.argv[1]
    align_results = sys.argv[1::2]
    names = sys.argv[2::2]
    tuples = zip(align_results, names)
    tuples = list(tuples)
    fig = plt.figure(figsize=(80, 70), dpi=150)
    ax = fig.add_subplot(111, projection='3d')  
    ax.view_init(elev=20., azim=190)
    
    print(i)


    #if i != len(tuples) - 1:
    #    format_axes(ax, hide=['top', 'right', 'left', "bottom"])
    #    ax.set_yticks([])
    #    ax.set_xticks([])
    #else:
    #format_axes(ax, hide=['top', 'right'], show=[ "bottom", 'left'])


    values = [
        sorted(get_values(hsh[0]), key=lambda x: x[0]) for hsh in tuples
    ]

    print(values[-1])
    values[-1].append(('unk', 1.0)) # patch
    values[-2].append(('unk', 1.0)) # patch
    print([
        len(v) for v in values
    ])

    first = values[0]
    xs = np.array(range(len(first)))
    ys = np.array(range(len(tuples)))

    zs = np.array(
        [[y[1] for y in x] 
        for x in values])
    
    print([np.mean([y[1] for y in x])
        for x in values])
    #zs = np.rot90(zs)
    print(zs)

    zs = zs.ravel()
    dx=0.2
    dy=0.2
    dz=zs
    xposM, yposM = np.meshgrid(xs, ys, copy=False)
    ax.w_xaxis.set_ticks(xs + dx/2.)
    ax.w_xaxis.set_ticklabels([f"n{i}" for i in range(len(first))])
    ax.set_xlabel("Edge nodes", fontsize=FONT_SIZE_LABEL)
    ax.xaxis.labelpad=LABEL_PAD

    ax.w_yaxis.set_ticks(ys + dy/2.)
    ax.w_yaxis.set_ticklabels([t[1].replace("_", "\_") for t in tuples], fontsize=FONT_SIZE_TICKS, 
    rotation=70, va='center', ha='right')
    #ax.set_ylabel("Endpoint", fontsize=FONT_SIZE_LABEL)

    ax.yaxis.labelpad=LABEL_PAD/6
    ax.tick_params(axis='y', which='major', pad=400)
    #ax.tick_params(axis='y', which='minor', pad=-420)
    ax.axes.set_zlim3d(bottom=0, top=1) 
    ax.w_zaxis.set_ticks(np.arange(0, 1.1, 0.1))
    ax.w_zaxis.set_ticklabels([f"{x:0.2f}" for x in np.arange(0, 1.1, 0.1)], fontsize=FONT_SIZE_TICKS)
    
    ax.set_zlabel("Unique traces ratio", fontsize=FONT_SIZE_LABEL)
    ax.zaxis.labelpad=LABEL_PAD
    ax.tick_params(axis='z', which='major', pad=70)

    colorvalues = np.linspace(0.2, 1., yposM.ravel().shape[0])
    colors = cm.viridis(colorvalues)

    ax.plot3D(
        xposM.ravel(),
        yposM.ravel(),
        dz,
        'o',
        linewidth=50,
        markersize=30
    )
    #ax.barh(
    #    range(len(values)),
    #    [x[1] for x in values],
    #    align="center"
    #)
    #ax.set_xlim(0, 1)
    #ax.set_yticklabels([x[0] for x in values])
    #ax.set_yticks(range(len(values)))
    
    print(values)

    #plt.show()
    plt.tight_layout()
    plt.savefig(f"out/hashes_collision3d.pops.pdf")
    #for ii in np.arange(0,360,10):
    #    ax.view_init(elev=10., azim=ii)
    #    plt.savefig("out/movie%d.png" % ii)


def draw_collisions():
    latexify(fig_width=14.5, fig_height=6.5, tick_size=20, font_size=15)


    all_values = []
    i = 1.5
    #name = sys.argv[1]
    align_results = sys.argv[1::2]
    names = sys.argv[2::2]
    tuples = zip(align_results, names)
    tuples = list(tuples)
    fig, axs = plt.subplots(nrows=2, ncols=math.ceil(len(tuples)/2),sharex=True, sharey=True)

    print(axs[0], len(tuples))
    if len(tuples) == 1:
        axs = [axs]
    #print(axs)
    axs = list(axs[0]) + list(axs[1]) # flatten for better usage
    for i, ax in enumerate(axs):
        print(i)
        if i >= len(tuples):
            ax.remove()
            continue

        hashes, name = tuples[i]
        hashes_DATA = json.loads(open(hashes, 'r').read())

        keys = [k for k in hashes_DATA.keys() if k != "endpoint"]
        map = [
            [0 for _ in range(len(keys))]
            for _ in range(len(keys))
        ]

        #if i != len(tuples) - 1:
        #    format_axes(ax, hide=['top', 'right', 'left', "bottom"])
        #    ax.set_yticks([])
        #    ax.set_xticks([])
        #else:
        format_axes(ax, hide=['top', 'right'], show=[ "bottom", 'left'])

        fname = hashes_DATA["endpoint"] if "endpoint" in hashes_DATA else name
        fname = fname.replace("_", "\_")


        for i,k in enumerate(keys):
            for j,k2 in enumerate(keys):
                if k != "endpoint" and k2 != "endpoint":
                    if k in hashes_DATA and k2 in hashes_DATA[k]["collisions"]:
                        map[i][j] = hashes_DATA[k]["collisions"][k2]

        COMPARISONS = [

        ]

        for i,k in enumerate(keys):
            for j in range(i + 1, len(keys)):
                k2 = keys[j]
                if k != "endpoint" and k2 != "endpoint":
                    if k in hashes_DATA and k2 in hashes_DATA[k]["collisions"]:
                        COMPARISONS.append(hashes_DATA[k]["collisions"][k2])

        print("Mean", np.mean(COMPARISONS), "Max", np.max(COMPARISONS), "Min", np.min(COMPARISONS))

        #print(values)
        ttl = ax.set_title(name.replace("_", "\_"), pad=20)
        ax.set_xticks([])
        ax.set_yticks([])

        #ax.set_xticks(range(len(keys)))
        #ax.set_yticks(range(len(keys)))

        names = [
            f"n{i}" for i in range(len(keys))
        ]
        #ax.set_xticklabels(names, rotation=-30, ha="right",
        #     rotation_mode="anchor")
        #ax.set_yticklabels(names)
        A = np.array(map)
        mask =  np.tri(A.shape[0], k=-1)
        A = np.ma.array(A, mask=mask).T # mask out the lower triangle
        im = ax.imshow(A)
        #print(im)
        ax.grid(which="minor", color="w", linestyle='-', linewidth=30)
        
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Equal traces", rotation=-90, va="bottom")


    plt.tight_layout()
    plt.savefig(f"out/hashes_collision_inter_pop.pdf")


def draw_entropy():
    latexify(fig_width=14.5, fig_height=6.5, tick_size=20, font_size=15)
    


if __name__ == "__main__":

    # draw_regular_violinplot()
    if not _3D:
        draw_histograms()
    else:
        draw_3d()

    if not PLOT_COLISSION_PER_PLOT_3D:
        draw_collisions()
    else:
        pass