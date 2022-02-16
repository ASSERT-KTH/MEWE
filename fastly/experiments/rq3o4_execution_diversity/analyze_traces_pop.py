from neo4j import GraphDatabase
import os
import sys
import json
from utils.utils import *
import hashlib

DIR=os.path.abspath(os.path.dirname(__file__))

SANITIZE_TRACES = True

def sanitize_trace(traces, PROJECTION_REVERSED):
    result = []
    

    for trace in traces:
        partial_result = []
        for s in trace:
            partial_result.append(PROJECTION_REVERSED[s])
            
        result.append(partial_result)
    return result

if __name__ == "__main__":

    data = json.loads(open(sys.argv[1], 'r').read())
    function_name = sys.argv[2]
    dispatcher_type = sys.argv[3]
    project = sys.argv[4]
    fmap = sys.argv[5]
    stablity = json.loads(open(sys.argv[6], 'r').read())

    fmap, reversed = parse_map(fmap)

    # Load stability report
    # sanitize the traces based on that

    d = data[function_name][dispatcher_type]

    paths = d['paths']
    fname = function_name

    OVERALL_RESULT={
        'endpoint':fname
    }
    for pop in paths:
        # fixed pop
        poppaths = paths[pop]
            
            
        traces = [p['path'] for p in poppaths if 'path' in p]
        if SANITIZE_TRACES:

            PROJECTION_REVERSED = classify_variants_based_on_preservation(fmap, reversed, stablity)

            traces = sanitize_trace(traces,PROJECTION_REVERSED)
        traces = [",".join([ f"{i}" for i in t ]) for t in traces]
        # hash the trace
        hsh = [hashlib.sha256(trace.encode()).hexdigest() for trace in traces]

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

    