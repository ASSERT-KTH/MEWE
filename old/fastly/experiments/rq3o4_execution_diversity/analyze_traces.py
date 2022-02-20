from neo4j import GraphDatabase
import os
import sys
import json
from utils.utils import *

DIR=os.path.abspath(os.path.dirname(__file__))
def generate_STRAC_payload(fname, traces):

    r = json.loads(open(f"{DIR}/default.json", 'r').read())
    OUTDIR=f"{DIR}/results/libsodium"

    files = []
    i = 0
    for t in traces:
        open(f"{OUTDIR}/STRAC_payloads/traces/{fname}.t.{i}.txt", 'w').write(t)
        files.append(f"traces/{fname}.t.{i}.txt")
        i += 1
    r['files'] = files
    r['outputAlignmentMap'] = f"{fname}.align.result.json"
    r['exportImage'] = True

    open(f"{OUTDIR}/STRAC_payloads/{fname}.payload.json", "w").write(json.dumps(r, indent=4))

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

if __name__ == "__main__":

    data = json.loads(open(sys.argv[1], 'r').read())
    function_name = sys.argv[2]
    dispatcher_type = sys.argv[3]
    project = sys.argv[4]

    fmap = sys.argv[5]
    fmap, reversed = parse_map(fmap)
    stablity = json.loads(open(sys.argv[6], 'r').read())

    # Load stability report
    # sanitize the traces based on that

    d = data[function_name][dispatcher_type]

    paths = d['paths']
    for pop in paths:
        # fixed pop
        poppaths = paths[pop]
        if pop != 'bma':
            continue

        OVERALL_PATH=set()
        for pathdict in poppaths:
            path = pathdict['path']
            #print(path)
            OVERALL_PATH.add(",".join([f"{p}" for p in path]))
            # entrypoint
            
        traces = [p['path'] for p in poppaths if 'path' in p]
        if SANITIZE_TRACES:
            traces = sanitize_trace(traces, stablity, fmap, reversed)
        traces = [",".join([ f"{i}" for i in t ]) for t in traces]
        generate_STRAC_payload(function_name, traces)

        print(function_name, len(OVERALL_PATH), len(poppaths))
        break

    