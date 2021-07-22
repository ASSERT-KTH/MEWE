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
from utils.dbutils import DBUtils

from multiprocessing import Pool

db = DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

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
    print(len(compressed), len(trace))

    #print(names_trace)
    mentioned = []
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


    stability_report = sys.argv[1]
    stability_report=json.loads(open(stability_report, 'r').read())

    funcname = sys.argv[2]
    fmap = sys.argv[3]
    fmap, reversed = parse_map(fmap) 

    trace = db.first("bma", funcname)['pathraw']# d["paths"]['bma'][0]['path']

    process(stability_report, trace, funcname, fmap)
    #print(involved_path_dispatchers("sodium_bin2base64"))

