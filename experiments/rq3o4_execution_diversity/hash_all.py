from neo4j import GraphDatabase
import os
import sys
import json
from utils.utils import *
from utils.dbutils import *
import time
import hashlib
SANITIZE_TRACES = True

DB=DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

DIR=os.path.abspath(os.path.dirname(__file__))

pops=["wdc","dca", "fty", "pdk", "akl", "bog", "bos", "eze", "ord", "ams", "maa", "chi", "mdw", "pwk", "cmh", "cph", "cwb", "dfw", "dal", "del", "den", "dub","fra", "hhn", "hel", "hkg", "iah", "jax", "jnb","mci", "lcy", "lhr", "lon", "bur", "lax", "mad", "man", "mrs", "mel", "mia", "stp", "yul", "bom","lga", "ewr", "itm", "osl", "pao", "cdg", "gig", "sjc", "scl", "cgh", "gru", "sea", "stl", "bma","syd", "tyo", "hnd", "yyz", "yvr", "vie"]


def sanitize_trace(traces, PRESERVATION_PROJECTION):
    
    result = []

    for trace in traces:
        partial_result = []
        for s in trace:
            try:
                partial_result.append(PRESERVATION_PROJECTION[s])
            except Exception as e:
                print(trace, s)
                raise e
        result.append(partial_result)
        
    return result

if __name__ == "__main__":

    function_name = sys.argv[1]
    stablity = json.loads(open(sys.argv[3], 'r').read())
    fmap = sys.argv[2]

    PRESERVATION_CACHE = calculate_preserved_cache(stablity)

    # Load stability report
    # sanitize the traces based on that

    #d = data[function_name][dispatcher_type]

    fname = function_name
    fmap, reversed = parse_map(fmap)

    OVERALL_RESULT={
        'endpoint':fname
    }
    # Pool maps all
    PROJECTION_REVERSED = classify_variants_based_on_preservation(fmap, reversed, stablity)
    for pop in pops:
        t0  = time.time()
        hshs = []
        i = 0
        if SANITIZE_TRACES:
            traces = []
            j = 0
            for t in DB.get_paths(
                popname=pop,
                casename=fname
            ):
                print(j)
                j += 1
                traces.append(t['pathraw'])


            traces = sanitize_trace(traces, PROJECTION_REVERSED)
            for t in traces:
                print(i)
                hsh = hashlib.sha256(t.__str__().encode()).hexdigest()
                hshs.append(hsh)
                i += 1
        else:
            for t in DB.get_paths(
                    popname=pop,
                    casename=fname
                ):

                print(i)
                i += 1
                hsh = hashlib.sha256(t.__str__().encode()).hexdigest()
                hshs.append(hsh)
        print(time.time() - t0)

        if pop not in OVERALL_RESULT:
            OVERALL_RESULT[pop] = dict(
                trace_hashes=hshs,
                unique_hashes=len(set(hshs)),
                total=len(hshs),
                
                collisions_set={

                },
                collisions={

                }
            )

        OVERALL_RESULT[pop]['ratio'] = OVERALL_RESULT[pop]['unique_hashes']/OVERALL_RESULT[pop]['total']
        # break
    # overall sum
    for k in pops:
        for k2 in pops:
            if k != k2:
                if k in OVERALL_RESULT and k2 in OVERALL_RESULT:
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

    