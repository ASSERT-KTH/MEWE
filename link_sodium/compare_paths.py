
import json
import sys
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib
from math import sqrt
SPINE_COLOR = 'gray'
plt.style.use('seaborn-colorblind')
import re

def filteroutliers(data):
    q1o = np.quantile(data, 0.1)
    q3o = np.quantile(data, 0.9)
    iqr = q3o - q1o
    q1o = q1o - 1.5*iqr
    q3o = q3o + 1.5*iqr
    data = filter(lambda x: x >= q1o and x <= q3o, data)

    return list(data)
def latexify(fig_width=None, fig_height=None, columns=1, font_size=8, tick_size=8):
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    #assert(columns in [1,2])

    if fig_width is None:
        fig_width = 3.7 if columns==1 else 6.9 # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0 # Aesthetic ratio
        fig_height = fig_width*golden_mean + 1.2 # height in inches

    #if fig_height > MAX_HEIGHT_INCHES:
    print(f"WARNING: fig_height too large: {fig_height}.")
    #print(matplotlib.rcParams.keys())
    pgf_with_latex = {                    # setup matplotlib to use latex for output
        "pgf.texsystem": "pdflatex",        # change this if using xetex or lautex
        "text.usetex": True,                # use LaTeX to write all text
        "font.family": "serif",
        "font.serif": [],                  # blank entries should cause plots
        "font.monospace": [],
        "axes.labelsize": font_size,               # LaTeX default is 10pt font.
        "font.size": font_size,
        "legend.fontsize": font_size,              # Make the legend/label fonts
        "xtick.labelsize": tick_size,              # a little smaller
        "ytick.labelsize": tick_size,
        "figure.figsize": [fig_width, fig_height],   # default fig size of 0.9 textwidth
        #"pgf.preamble": [
        #   r"\\usepackage[utf8x]{inputenc}",   # use utf8 fonts
        #   r"\\usepackage[T1]{fontenc}",       # plots will be generated
        #   r"\\usepackage[detect-all,locale=DE]{siunitx}",
        #   ]                                  # using this preamble
        }

    matplotlib.rcParams.update(pgf_with_latex)


def format_axes(ax, hide = ['top', 'right'], show= ['left', 'bottom']):

    for spine in hide:
        ax.spines[spine].set_visible(False)

    for spine in show:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)

    return ax


if __name__ == "__main__":
    latexify(fig_width=3.5, fig_height=3.5, font_size=12, tick_size=11)

    f = open(sys.argv[1])
    data = json.loads(f.read())
    MAX = 20000
    times = data['bin2base64']['pureRandom']['times'][0][:MAX]
    paths = data['bin2base64']['pureRandom']['times'][1][:MAX]

    MAX = 0
    PLOT_TPE = 'cumulative'
    groups = {}
    print("Samples", len(times))
    for t, path in zip(times, paths):
        #id = set(path).__str__()
        id = path[:1].__str__()
        #print(id)
        if id not in groups:
            groups[id] = []
        groups[id].append(t)
        
    if PLOT_TPE == 'cumulative':
        
        fig, axs = plt.subplots()
        ax1 = axs
        format_axes(ax1 ,hide=['top',  'right'], show=['left', 'bottom'])

        for k, ts  in groups.items():
            if len(ts) > 10:
                
                x = np.sort(ts)
                # scaling 
                x = x/1000 # microsecondss
                x = filteroutliers(x)
                xn = np.arange(1, len(x) + 1)/np.float(len(x))
                ax1.step(x, xn, alpha=0.1)
        ax1.set_xlabel("Execution time ($\mu$s)")
        ax1.set_ylabel("Cumulative density")
        
        # QQ plot
    elif PLOT_TPE == 'qqplot':
        # Also do a pairwise kolmogorov smirnov test
        F = False
        M = 100000
        GUIDE_ADDED = False
        cache = set()
        
        candidates = list(groups.items())
        S = 40 # len(groups)
        candidates = candidates[:S]
        print(S)
        fig, axs = plt.subplots()
        ax = axs
        format_axes(ax ,hide=['top', 'left', 'right', 'bottom'], show=[])
        
        mp = [[-1 for _ in range(S)] for _ in range(S)]
        for i, cand in enumerate(candidates):
            for j, cand2 in enumerate(candidates):
                k1, ts1 = cand
                k2, ts2 = cand2
                if k1 != k2 and j < i:
                    # fig = plt.figure()
                    percs = np.linspace(0,100,100)
                    # normalize

                    normts1 = stats.zscore(ts1)
                    normts2 = stats.zscore(ts2)

                    normts1 = filteroutliers(normts1)
                    normts2 = filteroutliers(normts2)


                    st, p = stats.ks_2samp(normts1, normts2)
                    mp[i][j] = p
            if F:
                pass
        mp = np.array(mp)
        masked =np.ma.masked_where(mp < 0, mp)

        cax = fig.add_axes([0.5, 0.2, 0.2, 0.05])        
        im = ax.imshow(masked)
        fig.colorbar(im, cax=cax, orientation='vertical')
    elif PLOT_TPE == 'box':

        fig, axs = plt.subplots()
        ax1 = axs
        times = []
        for k, ts  in groups.items():
            if len(ts) > 10:
                times.append(ts)
        ax1.violinplot(times)
    plt.tight_layout()
    plt.savefig("base64.pdf")
    plt.show()


    print(len(groups))

