from common.common import *
import numpy as np


def get_summaries(distributions, w=30):

    assert w <= 50

    summaries = []
    for distribution in distributions:
        m150l, m150r = np.percentile(distribution, 50-w),np.percentile(distribution, 50+w)
        print(m150l, m150r)
        summaries.append(np.average([m150l, m150r]))

    return summaries