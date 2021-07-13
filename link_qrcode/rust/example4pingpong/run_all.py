import sys
import os
import string
import shutil
from subprocess import check_output, Popen
import subprocess
import requests
import json
import sys

import urllib3
from extract_wasm_stats import process as process_wasm_stats
import traceback
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

urllib3.disable_warnings()

def deploy(mainContent, bitcodes_folder="original", save_as=None, save_sec_as="sec.txt"):
    print(f"Deploying {mainContent} {bitcodes_folder} {save_as}")

    #shutil.rmtree("target")
    open("src/main.rs", 'w').write(mainContent)
    # executing deploy script

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

def execute_to_time(service_name, times=100):

    result = []
    print("Getting execution time distribution")
    for t in range(times):
        response = requests.get(service_name)
        result.append(int(response.headers["xtime"]) if 'xtime' in response.headers else -1)
        if 'xtime' in response.headers:
            print(response.headers['xtime'])

    return result


cache = {

}

BLACKLIST = ["mxp", "lck", "msp", "sin"]

def execute_paths(service_name, t=1):
    global cache

    print("Getting execution paths")
    POPS = json.loads(open(f"{sys.argv[1]}/pops.json", 'r').read())
    results = {

    }
    retry_strategy = Retry(
        total=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    for _ in range(t):
        for i, pop in enumerate(POPS):
            popl = pop["code"].lower()

            if popl in BLACKLIST:
                continue

            print(i, len(POPS), popl)
            # try machines until it executes succesfully
            if os.path.exists(f"{sys.argv[1]}/range_{popl}.json"):
                machines = json.loads(open(f"{sys.argv[1]}/range_{popl}.json", 'r').read())

                for j, machine in enumerate(machines["valid"]):

                    if popl in cache:
                        pcNumber = cache[popl]
                    else:
                        pcNumber = machine["at"]

                    #print("\r%s %s"%(j, len(machines['valid'])))
                    try:
                        response = http.get(
                            f"https://cache-{popl}{pcNumber}.hosts.secretcdn.net",
                            headers={
                                'Host': service_name
                            },
                            verify=False,
                            timeout=20
                        )
                        content = response.text
                        #print(response.headers)
                        #print(content)
                        path = eval(content)
                        print(len(path))
                        time = response.headers['xtime']
                        if popl not in results:
                            results[popl] = []
                        results[popl].append({
                            'content': "<QRCODE>",
                            'path': path,
                            'time': time
                        })
                        
                        print("Gotcha", popl, pcNumber, f"{time}ns")
                        cache[popl] = pcNumber
                        break
                    except KeyboardInterrupt:
                        return results
                    except Exception as e:
                        print(e)
                        if popl in cache and pcNumber == cache[popl]:
                            del cache[popl]

    return results

def test_with_template(case, template_name, extract_paths=True, extract_times=True, bitcodes_folder="instrumented", t=1):
    mname, _   = case

    MAIN_TEMPLATE = open(f"templates/{template_name}", 'r').read()


    # test entry path
    rPathMain = MAIN_TEMPLATE

    rPathSize, meta, secmeta = deploy(rPathMain, bitcodes_folder, save_as=f"{mname}_d.wasm" if extract_paths else f"{mname}_paths.wasm", save_sec_as=f"{mname}{extract_paths}{extract_times}{bitcodes_folder}.sec.txt")

    #open(, 'w').write(secmeta)

    print("rPath size", rPathSize)
    times = execute_to_time("https://totally-devoted-krill.edgecompute.app") if extract_times else { }
    paths = execute_paths("totally-devoted-krill.edgecompute.app", t=t) if extract_paths else []

    return dict(
        paths=paths,
        times=times,
        packageSize=rPathSize,
        meta = meta
    )

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
    withrPathTimes = execute_to_time("https://totally-devoted-krill.edgecompute.app")

    return dict(
        paths={},
        times=withrPathTimes,
        packageSize=rPathSize,
        meta = meta
    )

def test_case(case):
    fname, cases = case
    print("testing", fname)
    original, instrumented, multivariant = cases
    # pureley random

    print("Instrumented")
    multivariant_bc, template = instrumented
    instrumentedPureRandom = test_with_instrumentation(case, template=template, times=100, bitcode=multivariant_bc)
    

    print("Original libsodium")
    bc, template = original
    noDivResults = test_no_diversification(fname, bitcode=bc, template=template) # template f"templates/main_single.rs"
    
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
            "run_qr_str",[
            ("all.bc", "main.rs"), # original
            ("allinone.multivariant.i.bc", "instrumented_str.rs"), # instrumented for path
            ("allinone.multivariant.bc", "main.rs")] # multivariant
        ),
        (
            "run_qr",[
            ("all.bc", "main_bytes.rs"), # original
            ("allinone.multivariant.i.bc", "instrumented.rs"), # instrumented for path
            ("allinone.multivariant.bc", "main_bytes.rs")] # multivariant
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

            # Save single case
            if not os.path.exists(f"results"):
                os.mkdir("results")

            open(f"results/{case[0]}.result.json", 'w').write(
                json.dumps(
                    {
                        case[0]: dict(
                            original=original,
                            instrumented=instrumented,
                            nonInstrumented=nonInstrumented,
                            instrumentedDeterministic=instrumentedDeterministic,
                            nonInstrumentedDeterministic=nonInstrumentedDeterministic,
                            instrumentedPureRandom=instrumentedPureRandom,
                            pureRandom=pureRandom
                        )
                    }
                )
            )

            #print(original["packageSize"], instrumented["packageSize"], nonInstrumented["packageSize"])
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

    open("cache.json", 'w').write(json.dumps(cache))