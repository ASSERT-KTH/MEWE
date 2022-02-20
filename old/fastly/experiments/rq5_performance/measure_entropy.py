import sys
from latexify.common import *
from itertools import zip_longest
import matplotlib.pyplot as plt
import json
import numpy as np
from scipy.optimize import curve_fit
import scipy.stats as stats
import math
from utils.utils import *

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




    for i in range(len(tuples)):

        fname, times, title = tuples[i]

        #print(times)
        original, mult = times
        original = [t for t in original if t != -1]
        mult = [t for t in mult if t != -1]
        
        e1, s1 = get_entropy(original)
        e2, s2 = get_entropy(mult)
        print(fname)
        print(e1, s2, e2, s2)

        print()

