import sys
import redis
from multiprocessing import Pool
from neo4j import GraphDatabase

import subprocess

import json
import os
import time
import platform
import hashlib
import re
import base64 as b64
import functools
from utils.utils import *

from multiprocessing import Pool


WHITE_LIST=[]


def process(data, trace, funcname, fmap, popname="ams"):
    #print(trace)
    # remove cycles
    next = trace[1::]
    next = [
        fmap[t]['parent'] for t in next
    ]
    prev = trace[:-1:]

    prev = [
        fmap[t]['parent'] for t in prev
    ]

    tuples = zip(prev, next)

    compressed = [ next for prev,next in tuples if prev != next]
    compressed += [fmap[trace[0]]['parent']] # the first symbol is always dropped
    #return
    #print(compressed)
    mentioned = []
    print(len(compressed), len(trace))

    #print(names_trace)
    MULT_W = 1
    MULT_N = 1
    for name in compressed:
        W1,N1 = get_preservation_for_function(data, name)
        if N1 > 1 and name not in mentioned:
            print(name, N1)
            MULT_N *= N1
            mentioned.append(name)

    print(funcname, MULT_N)
if __name__ == "__main__":

    trace_data = sys.argv[1]
    trace_data=json.loads(open(trace_data, 'r').read())

    stability_report = sys.argv[2]
    stability_report=json.loads(open(stability_report, 'r').read())

    funcname = sys.argv[3]
    fmap = sys.argv[4]
    fmap, reversed = parse_map(fmap) 

    d = trace_data[funcname]["instrumentedPureRandom"]

    trace = d["paths"]['bma'][0]['path']
    process(stability_report, trace, funcname, fmap)
    #print(involved_path_dispatchers("sodium_bin2base64"))

