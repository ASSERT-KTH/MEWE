from neo4j import GraphDatabase
import os
import sys
import json

def generate_STRAC_payload(fname, traces):

    r = json.loads(open("default.json", 'r').read())

    files = []
    i = 0
    for t in traces:
        open(f"STRAC_payloads/traces/{fname}.t.{i}.txt", 'w').write(t)
        files.append(f"traces/{fname}.t.{i}.txt")
        i += 1
    r['files'] = files
    r['outputAlignmentMap'] = f"{fname}.align.result.json"
    r['exportImage'] = True

    open(f"STRAC_payloads/{fname}.payload.json", "w").write(json.dumps(r, indent=4))

if __name__ == "__main__":

    data = json.loads(open(sys.argv[1], 'r').read())
    function_name = sys.argv[2]
    dispatcher_type = sys.argv[3]
    project = sys.argv[4]
    fmap = json.loads(open(sys.argv[5], 'r').read())

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
        traces = [",".join([ f"{i}" for i in t ]) for t in traces]
        generate_STRAC_payload(function_name, traces)

        print(function_name, len(OVERALL_PATH), len(poppaths))
        break

    