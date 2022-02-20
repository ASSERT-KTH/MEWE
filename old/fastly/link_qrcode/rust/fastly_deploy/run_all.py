import sys
import os
import string
import shutil
from subprocess import check_output, Popen
import subprocess
import requests
import json
import sys
# import gridfs
import urllib3
from extract_wasm_stats import process as process_wasm_stats
import traceback
from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
import pymongo
from multiprocessing import Pool
from itertools import zip_longest
import hashlib
# from pympler import tracker

MONGO_USER=os.environ.get("MONGO_USER")
MONGO_PASS=os.environ.get("MONGO_PASS")

myclient = None # pymongo.MongoClient(f"mongodb://{MONGO_USER}:{MONGO_PASS}@localhost:27017/")
mydb = None #myclient["fastly4edge"]

fs = None #gridfs.GridFS(mydb)


urllib3.disable_warnings()

def deploy(mainContent, bitcodes_folder="original", save_as=None, save_sec_as="sec.txt"):
    print(f"Deploying {mainContent} {bitcodes_folder} {save_as}")

    #shutil.rmtree("target")
    open("src/main.rs", 'w').write(mainContent)
    # executing deploy script
    print("bash",
            "build.sh",
            os.getenv("SERVICE_ID"),
            bitcodes_folder)
    out = subprocess.Popen(
        [
            "bash",
            "build.sh",
            os.getenv("SERVICE_ID"),
            bitcodes_folder
        ]
        ,stderr=subprocess.PIPE,
        stdout=subprocess.PIPE
    )
    out.wait()

    stdout, stderr = out.communicate()
    print(stdout.decode())

    print(stderr.decode())

    # check file size
    wasmSize = len(open("example_qr.wasm", 'rb').read())
    try:
        metadata = process_wasm_stats("example_qr.wasm")
    except:
        metadata = { }
    if save_as:
        shutil.copy("example_qr.wasm", f"out/{save_as}")
    # execute wasmbench security analysis tool

    
    return wasmSize, metadata, out

def execute_to_time(service_name, times=1, meta={}):

    result = []
    dispatchers = []

    print("Getting execution time distribution")
    for t in range(times):
        try:
            response = requests.get(service_name)
            result.append(int(response.headers["xtime"]) if 'xtime' in response.headers else -1)
            if 'xtime' in response.headers:
                print(t, response.headers['xtime'])
            if 'xdispatcher' in response.headers:
                    # print(response.headers['xdispatcher'])
                dispatchers.append(eval(response.headers["xdispatcher"]) if 'xtime' in response.headers else [])
        except KeyboardInterrupt:
            break
    # Save 
    return result,dispatchers


cache = {

}

BLACKLIST = ["mxp", "lck", "msp", "sin"]
def pex(p):
    
    if os.path.exists("cache.json"):
        cache = json.loads(open("cache.json", 'r').read())

    i, pop, POPS, service_name, http, times, meta = p
    popl = pop["code"].lower()


    print(i, len(POPS), popl)
    # try machines until it executes succesfully
    #if os.path.exists(f"{sys.argv[1]}/range_{popl}.json"):
        # machines = json.loads(open(f"{sys.argv[1]}/range_{popl}.json", 'r').read())

        #for j, machine in enumerate(machines["valid"]):

    if popl in cache:
        pcNumber = cache[popl]
    else:
        return 
        #else:
        #    pcNumber = machine["at"]

        #print("\r%s %s"%(j, len(machines['valid'])))
    print("executing", pcNumber, popl)
    try:
        for _ in range(times):
            response = http.get(
                f"https://cache-{popl}{pcNumber}.hosts.secretcdn.net",
                headers={
                    'Host': service_name
                },
                verify=False,
                timeout=8
            )
            content = response.text
            #print(response.headers)
            #print(content)
            path = eval(content)
            print(len(path))
            time = response.headers['xtime']
            print("Gotcha", popl, pcNumber, f"{time}ns")
            record = {
                'content': "<QRCODE>",
                'path': save_large(path),
                'time': time,
                'pop': popl,
                **meta
            }
            paths = mydb["paths"]
            
            print("Saving in db...", popl)
            x = paths.insert_one(record)
            print(x)
    except KeyboardInterrupt:
        return 

    except Exception as e:
        print(e)

            #if popl in cache and pcNumber == cache[popl]:
            #    del cache[popl]

def save_large(content):
    f = fs.put(json.dumps(content).encode())
    return f

def execute_paths(service_name, t=1, meta={}):
    

    print("Getting execution paths")
    POPS = json.loads(open(f"{sys.argv[1]}/pops.json", 'r').read())
    
    retry_strategy = Retry(
        total=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    results = {}                                                                                                                                                                                                                                                                                                                                      
    #
    #POPS=POPS[:2]
    with Pool(20) as pool:
        # results, POPS, service_name, http
        params = zip_longest(
            range(len(POPS)),
            POPS, 
            [POPS]*len(POPS),
            [service_name]*len(POPS),
            [http]*len(POPS),
            [t]*len(POPS),
            [meta]*len(POPS)

        )
        pool.map(pex, 
            params
        )   

    return results

def test_with_template(case, template_name, extract_paths=True, extract_times=True, bitcodes_folder="instrumented", t=1):
    mname, _   = case

    MAIN_TEMPLATE = open(f"templates/{template_name}", 'r').read()


    # test entry path
    rPathMain = MAIN_TEMPLATE

    rPathSize, meta, secmeta = deploy(rPathMain, bitcodes_folder, save_as=f"{mname}_d.wasm" if not extract_paths else f"{mname}_paths.wasm", save_sec_as=f"{mname}{extract_paths}{extract_times}{bitcodes_folder}.sec.txt")

    #open(, 'w').write(secmeta)

    print("rPath size", rPathSize)

    record = dict(
        casename=mname,
        packageSize=rPathSize,
        case=case,
        session=os.environ.get("SESSION_ID"),
        meta=dict(
            folder=bitcodes_folder,
            extract_paths=extract_paths,
            extract_times=extract_times,
            template_name=template_name,
            **meta
        ),
        tpe="multivariant" if not execute_paths else "instrumented",
    )

    times = execute_to_time("https://totally-devoted-krill.edgecompute.app", meta=record, times=60000) if extract_times else { }
    paths = execute_paths("totally-devoted-krill.edgecompute.app", t=t, meta=record) if extract_paths else []

    execs = mydb["execs"]
    record['paths']= save_large(paths)
    record['times'] = save_large(times)
    print("Saving in db...")
    x = execs.insert_one(record)
    print(x)
    return record

def test_with_instrumentation(case, template="main.rs", bitcode="all.bc", times=1):
    return test_with_template(case, template, extract_times=False, bitcodes_folder=bitcode, t=times)

def test_without_instrumentation(case, template="main_4_time.rs", bitcode="all.bc"):
    return test_with_template(case, template, extract_times=True, extract_paths=False, bitcodes_folder=bitcode)

def test_no_diversification(name, bitcode, template):
    # mname, module, usage, entry4Path, entry4time, importNoDiversification, entryNoDiversification, module  = case

    MAIN_TEMPLATE = open(f"templates/{template}", 'r').read()


    # test entry path
    rPathMain = MAIN_TEMPLATE

    rPathSize, meta, secmeta = deploy(rPathMain,  bitcodes_folder=bitcode, 
    save_as=f"{name}_original.wasm", save_sec_as=f"{name}.regular.sec.txt")
    #open(f"{mname}.regular.sec.txt", 'w').write(secmeta)

    print("rPath size", rPathSize)
    withrPathTimes = execute_to_time("https://totally-devoted-krill.edgecompute.app", times=10000)

    execs = mydb["execs"]

    record = dict(
        
        paths={},
        times=save_large(withrPathTimes),
        packageSize=rPathSize,
        name=name,
        session=os.environ.get("SESSION_ID"),
        meta=dict(
            folder=bitcode,
            template=template,
            **meta
        ),
        tpe="original"
    )
    x = execs.insert_one(record)

    return record

def test_case(case):
    fname, cases = case
    print("testing", fname)
    original, instrumented, multivariant = cases
    # pureley random

    print("Instrumented")
    multivariant_bc, template = instrumented
    instrumentedPureRandom = None  # test_with_instrumentation(case, template=template, times=100, bitcode=multivariant_bc)
    

    print("Original qr")
    bc, template = original
    noDivResults = None # test_no_diversification(fname, bitcode=bc, template=template) # template f"templates/main_single.rs"
    
    print("Random dispatcher")
    multivariant_bc, template = multivariant
    pureRandom = test_without_instrumentation(case, template=template, bitcode=multivariant_bc)

    #print("Instrumented diversifier deterministic ")
    instrumentedDeterministicResults = None
    #print("Non instrumented diversifier deterministic")
    nonInstrumentedDeterministicResults = None #print("Instrumented diversifier based on hashing")
    instrumentedResults = None
    #print("Diversifier based on hashing")
    nonInstrumentedResults = None


    return noDivResults, instrumentedResults, nonInstrumentedResults, instrumentedDeterministicResults, nonInstrumentedDeterministicResults, instrumentedPureRandom, pureRandom

def test_all():
    
    cases = [
        (
            "run_qr",[
            ("all.bc", "main_bytes.rs"), # original
            ("allinone.multivariant.i.bc", "instrumented.rs"), # instrumented for path
            ("allinone.multivariant.bc", "main_bytes.rs")] # multivariant
        ),
        (
            "run_qr_str",[
            ("all.bc", "main.rs"), # original
            ("allinone.multivariant.i.bc", "instrumented_str.rs"), # instrumented for path
            ("allinone.multivariant.bc", "main.rs")] # multivariant
        )
        
    ]

    OVERALL = dict()
    for case in cases:
        try:
            original, instrumented, nonInstrumented, instrumentedDeterministic, nonInstrumentedDeterministic, instrumentedPureRandom, pureRandom = test_case(case)

            OVERALL[case[0]] = dict(
                original=original,
                instrumented=instrumented,
                nonInstrumented=nonInstrumented,
                instrumentedDeterministic=instrumentedDeterministic,
                nonInstrumentedDeterministic=nonInstrumentedDeterministic,
                instrumentedPureRandom=instrumentedPureRandom,
                pureRandom=pureRandom
            )

            #break

            # Save single case
            if not os.path.exists(f"results"):
                os.mkdir("results")
        except Exception as e:
            print("Error",case[0], e, traceback.format_exc())

    open("results.json", 'w').write(json.dumps(OVERALL, indent=4))

if __name__ == "__main__":

    try:
        if os.path.exists("cache.json"):
            cache = json.loads(open("cache.json", 'r').read())
        print(cache)
        test_all()
    except KeyboardInterrupt:
        pass

