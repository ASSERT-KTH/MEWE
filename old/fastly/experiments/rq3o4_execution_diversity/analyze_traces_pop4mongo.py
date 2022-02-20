from neo4j import GraphDatabase
import os
import sys
import json
from utils.utils import *
from utils.dbutils import *
import time
import hashlib

DB=DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

DIR=os.path.abspath(os.path.dirname(__file__))

SANITIZE_TRACES = True

def sanitize_trace(traces, stability_data, fmap, reversed):
    result = []
    PRESERVATION_COUNT = {

    }
    classes = {  }

    # create equivalence classes
    for k, fname in fmap.items():
        W,N = get_preservation_for_function(stability_data, fname['parent'])
        if not fname['parent']:
            raise Exception(f"{fname}")
        PRESERVATION_COUNT[fname['parent']] = N

    for k, fname in fmap.items():
        if PRESERVATION_COUNT[fname['parent']] > 0:
            # it is a different variant
            classes[k] = k
            PRESERVATION_COUNT[fname['parent']] -= 1
        else:
            classes[k] = reversed[fname['parent']]['group']


    for trace in traces:
        partial_result = []
        for s in trace:
            partial_result.append(classes[s])
            
        result.append(partial_result)
    return result


pops=["wdc","dca", "fty", "pdk", "akl", "bog", "bos", "eze", "ord", "ams", "maa", "chi", "mdw", "pwk", "cmh", "cph", "cwb", "dfw", "dal", "del", "den", "dub","fra", "hhn", "hel", "hkg", "iah", "jax", "jnb","mci", "lcy", "lhr", "lon", "bur", "lax", "mad", "man", "mrs", "mel", "mia", "stp", "yul", "bom","lga", "ewr", "itm", "osl", "pao", "cdg", "gig", "sjc", "scl", "cgh", "gru", "sea", "stl", "bma","syd", "tyo", "hnd", "yyz", "yvr", "vie"]

if __name__ == "__main__":

    function_name = sys.argv[1]
    stablity = json.loads(open(sys.argv[3], 'r').read())
    fmap = sys.argv[2]

    # Load stability report
    # sanitize the traces based on that
    fmap, reversed = parse_map(fmap)

    #d = data[function_name][dispatcher_type]

    fname = function_name

    OVERALL_RESULT={
        'endpoint':fname
    }
    for pop in pops:
        # fixed pop
        #poppaths = paths[pop]
            
            
        #traces = [p['path'] for p in poppaths if 'path' in p]
        #if SANITIZE_TRACES:
        #    traces = sanitize_trace(traces, stablity, fmap, reversed)
        #traces = [",".join([ f"{i}" for i in t ]) for t in traces]
        # hash the trace
        t0  = time.time()
        for t in DB.get_paths(
                popname=pop,
                casename=fname
            ):
            hsh = hashlib.sha256(t.__str__().encode()).hexdigest()
            print(hsh)
            break
        print(time.time() - t0)

        #hsh = [hashlib.sha256(",".join(trace).encode()).hexdigest() for trace in ]

        if pop not in OVERALL_RESULT:
            OVERALL_RESULT[pop] = dict(
                trace_hashes=hsh,
                unique_hashes=len(set(hsh)),
                total=len(hsh),
                
                collisions_set={

                },
                collisions={

                }
            )

        OVERALL_RESULT[pop]['ratio'] = OVERALL_RESULT[pop]['unique_hashes']/OVERALL_RESULT[pop]['total']
    # overall sum

    for k in paths:
        for k2 in paths:
            if k != k2:
                hsh1 = OVERALL_RESULT[k]["trace_hashes"]
                hsh2 = OVERALL_RESULT[k2]["trace_hashes"]
                #print(OVERALL_RESULT[k]['trace_hashes'], OVERALL_RESULT[k2])
                intersection = set(hsh1).intersection(set(hsh2))
                print(k, k2, len(intersection))
                OVERALL_RESULT[k]["collisions_set"][k2] = len(intersection)
                OVERALL_RESULT[k]["collisions"][k2] = len([
                    x for x in hsh1 if x in hsh2
                ])


    #print(OVERALL_RESULT)
    open(f"{DIR}/results/rq4/{fname}.rq4.json", 'w').write(json.dumps(OVERALL_RESULT, indent=4))

    