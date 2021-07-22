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
import numpy as np
from utils.dbutils import DBUtils

DB = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

def get_entropy_from_file(fname, jsonfile, fmap, stability, breakatfirst=True):
    paths = json.loads(open(jsonfile, 'r').read())

    
    p = paths[fname]['instrumentedPureRandom']['paths']
    overall = []
    distribution = []
    dispatchers = set()
    dispatchers_distrib = {}

    for i in range(100):
        try:
            for pop, k in p.items():
                overall += k[i]['path']
                distribution.append(len(k[i]['path']))

                if breakatfirst:
                    break
            if breakatfirst:
                break
        except Exception as e:
            print(e, pop)
            pass
    #print(len(overall))
    # overall = [1,2,2,1]
    entropy = get_entropy(overall)

    for s in overall:
        f = fmap[s]
        if f['isDispatcher']:
            p, r = get_preservation_for_function(stability, f['parent'])
            
            if r > 1:
                dispatchers.add(f['parent'])
                if f['parent'] not in dispatchers_distrib:
                    dispatchers_distrib[f['parent']] = 0
                dispatchers_distrib[f['parent']] += 1

    print()
    print(len(dispatchers_distrib), sum(v for k, v in dispatchers_distrib.items()) *(6400 if breakatfirst else 1))
    print(np.median(distribution), np.std(distribution) )
    # calcuate how many dispatchers ?
    return entropy


def get_entropy_from_db(fname, jsonfile, fmap, stability, breakatfirst = True):
    M = DB.count_all_paths(casename=fname, sessionname="final2")

    print(M)
    FREQ = {}
    LEN=0
    it = 0

    distribs = []
    dispatchers = set()
    dispatchers_distrib = {}
    L1 = 0

    def calculate(FREQ, LEN):
        PROBS = {}

        for p in FREQ:
            PROBS[p] = FREQ[p]/LEN
        

        E = 0

        for p in PROBS:
            E += -1*PROBS[p]*log(PROBS[p], 2) #32 bits per function id
        
        RI = len(PROBS.keys())
        if len(PROBS.keys())== 0:
            return E, 0
        return E, E/log(RI,2)

    for t in DB.get_all_paths(casename=fname, sessionname="final2"):
        
        LEN += len(t['pathraw'])
        distribs.append(len(t['pathraw']))
        sys.stdout.write(f"\r{it}/{M}")
        if L1 == 0:
            L1 = sum(v for k, v in dispatchers_distrib.items())
        if it % 20 == 0 and it > 0:
            print()
            print(np.median(distribs), np.std(distribs), dispatchers_distrib, sum(v for k, v in dispatchers_distrib.items()))
            if np.std(distribs) == 0:
                break
        for s in t['pathraw']:
            #if s not in FREQ:
            #    FREQ[s] = 0
            #FREQ[s] += 1
            f = fmap[s]
            if f['isDispatcher']:
                p, r = get_preservation_for_function(stability, f['parent'])
                
                if r > 1:
                    dispatchers.add(f['parent'])
                    
                    if f['parent'] not in dispatchers_distrib:
                        dispatchers_distrib[f['parent']] = 0
                    dispatchers_distrib[f['parent']] += 1

        if breakatfirst:
            break
        it += 1
    

    print()
    print(L1, np.median(distribs), np.std(distribs), len(dispatchers_distrib), sum(v for k, v in dispatchers_distrib.items())*(6400 if breakatfirst else 1))
    
    #if breakatfirst:
    #    for k, v in dispatchers_distrib.items():
    #        print(k)
    return 1,1 

def draw_entropy():
    latexify(fig_width=14.5, fig_height=6.5, tick_size=20, font_size=15)
    
    fmap, reversed = parse_map(sys.argv[1])
    stability= json.loads(open(sys.argv[2], 'r').read())
    fnames = sys.argv[3::3]
    jsons = sys.argv[4::3]
    tpes = sys.argv[5::3]

    tuples = zip_longest(fnames, jsons, tpes)

    for fname, js, tpe in tuples:
        print(fname, tpe)
        e = 0
        if tpe == "file":
            e = get_entropy_from_file(fname, js, fmap, stability)
        if tpe == "db":
            e = get_entropy_from_db(fname, fname, fmap, stability)
        print(e)
    
def draw_entropy_on_trace_unit():
    fnames = sys.argv[2::2]
    jsons = sys.argv[1::2]
    jsons = [json.loads(open(j, 'r').read()) for j in jsons]

    tuples = zip_longest(fnames, jsons)
    for name, j in tuples:
        print(name)
        OVERALL = []
        for k, v in j.items():
            if k != 'endpoint':
                #print(len(v["trace_hashes"]))
                OVERALL += v["trace_hashes"]
        entropy = get_entropy(OVERALL)
        print(entropy)
        # break

if __name__ == "__main__":

    #draw_entropy_on_trace_unit()
    # 
    draw_entropy()