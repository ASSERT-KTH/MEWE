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
from itertools import zip_longest
from utils.utils import *
from math import log
from utils.dbutils import DBUtils

DB = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

def get_entropy_from_file(fname, jsonfile):
    paths = json.loads(open(jsonfile, 'r').read())

    
    p = paths[fname]['instrumentedPureRandom']['paths']
    overall = []

    for i in range(100):
        try:
            for pop, k in p.items():
                overall += k[i]['path']
        except Exception as e:
            print(e, pop)
            pass
    #print(len(overall))
    # overall = [1,2,2,1]
    entropy = get_entropy(overall)

    return entropy


def get_entropy_from_db(fname, jsonfile):
    M = DB.count_all_paths(casename=fname)

    FREQ = {}
    LEN=0
    it = 0

    def calculate(FREQ, LEN):
        PROBS = {}

        for p in FREQ:
            PROBS[p] = FREQ[p]/LEN
        

        E = 0

        for p in PROBS:
            E += -1*PROBS[p]*log(PROBS[p], 2) #32 bits per function id
        
        RI = len(PROBS.keys())
        return E, E/log(RI,2)

    for t in DB.get_all_paths(casename=fname):
        
        LEN += len(t['pathraw'])
        sys.stdout.write(f"\r{it}/{M}")
        if it % 20 == 0 and it > 0:
            print(calculate(FREQ, LEN))
        for s in t['pathraw']:
            if s not in FREQ:
                FREQ[s] = 0
            FREQ[s] += 1
        it += 1
    
    return calculate(FREQ, LEN)

def draw_entropy():
    latexify(fig_width=14.5, fig_height=6.5, tick_size=20, font_size=15)
    
    fnames = sys.argv[1::3]
    jsons = sys.argv[2::3]
    tpes = sys.argv[3::3]

    tuples = zip_longest(fnames, jsons, tpes)

    for fname, json, tpe in tuples:
        print(fname, tpe)
        e = 0
        if tpe == "file":
            e = get_entropy_from_file(fname, json)
        if tpe == "db":
            e = get_entropy_from_db(fname, fname)
        print(e)
    

if __name__ == "__main__":

    draw_entropy()