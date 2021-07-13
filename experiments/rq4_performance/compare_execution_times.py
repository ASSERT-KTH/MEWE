import sys
from latexify.common import *
from itertools import zip_longest
import matplotlib.pyplot as plt
import json
import numpy as np
from scipy.optimize import curve_fit
import scipy.stats as stats
import math

DRAW_CURVE_OVER=False

def get_times(jsonfile, func, original, random):
    data = json.loads(open(jsonfile, 'r').read())
    timesOriginal = data[func][original]['times']
    timesmultivariant = data[func][random]['times']

    return timesOriginal, timesmultivariant
if __name__ == "__main__":
    tpe = sys.argv[1]

    args = dict()
    common_args = dict(
        bins="auto"
    )
    if tpe == "density":
        args = dict(
            density=True,
            #histtype="step"
        )

    payloads = sys.argv[2::5]
    function = sys.argv[3::5]
    original = sys.argv[4::5]
    multivariant = sys.argv[5::5]
    titles = sys.argv[6::5]
    tuples = zip_longest(
        payloads,
        function,
        original,
        multivariant,
        titles
    )


    tuples = [
        (
            t[1], # funcname,
            get_times(t[0], t[1], t[2], t[3]),
            t[-1] # tilte
        ) for t in tuples
    ]


    latexify(fig_width=9, fig_height=5.5)


    fig, axs = plt.subplots(nrows=3, ncols=3, sharex=False)

    axs = list(axs[0]) + list(axs[1])  + list(axs[2])
    for i in range(len(axs)):
        ax = axs[i]
        if i >= len(function):
            ax.remove()
            continue

        format_axes(ax, show=['bottom'], hide=['left', 'top', 'right'])
        fname, times, title = tuples[i]

        #print(times)
        original, mult = times
        original = [t for t in original if t != -1]
        mult = [t for t in mult if t != -1]

        #print(original, mult)

        tendency = lambda x: np.median(x)
        r=tendency(mult)/tendency(original)
        print(fname,f"x{r}", tendency(original), tendency(mult), stats.mannwhitneyu(original, mult))

        no, binso, patcho = ax.hist(original, bins="auto", alpha=0.3, color="C0", **args)

        nm, binsm, patchm = ax.hist(mult, bins="auto", color="C1", alpha=0.3, **args)

        # Draw curve over
        if DRAW_CURVE_OVER:
            gaussian_kde_zi = stats.gaussian_kde(original)
            gaussian_kde_zi.covariance_factor = lambda : 0.3
            gaussian_kde_zi._compute_covariance()
            x=np.linspace(min(original), max(original), 10000)
            ax.plot(x, gaussian_kde_zi(x),  linewidth=1, label='kde', color="C0")
            
            gaussian_kde_zz = stats.gaussian_kde(mult)
            gaussian_kde_zz.covariance_factor = lambda : 0.3
            gaussian_kde_zz._compute_covariance()
            x=np.linspace(min(mult), max(mult), 10000)
            ax.plot(x, gaussian_kde_zz(x),  linewidth=1, label='kde', color="C1")


                # original_curvex, original_curve_y = curve_params(no, binso, patcho)
                #ax.plot(original_curvex, original_curve_y)
        ax.set_title(title.replace("_", "\_"))
        if i == len(function) - 1:
            ax.legend([
                    "Original binary",
                    "Multivariant binary"
                ], bbox_to_anchor = (0.5,-0.3)
            )
        ax.set_yticks([])
        ax.set_xlabel("Execution time (ns)")
        ax.set_ylabel("Density")
        # ax.set_ylabel("Execution time (ns)")

    
    plt.tight_layout()
    plt.savefig(f"out/times.pdf")

