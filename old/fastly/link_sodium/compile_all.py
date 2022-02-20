import sys
import os
import string
import shutil
from subprocess import PIPE, check_output, Popen
import subprocess
import requests
import json
import sys

import urllib3
from cases import *
from extract_wasm_stats import process as process_wasm_stats
import traceback
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

urllib3.disable_warnings()

# set TEST=False to avoid exhasutive test
TEST=True

def deploy(mainContent, bitcodes_folder="inlined/original", save_as=None, save_sec_as="sec.txt", instrument_small_check=True):
    print("Deploying", bitcodes_folder)

    #shutil.rmtree("target")
    open("src/main.rs", 'w').write(mainContent)
    # executing deploy script

    try:
        print("Executing...", "bash build_4fastly.sh", 
                os.getenv("SERVICE_ID"), bitcodes_folder)
        p = subprocess.Popen(
            [
                "bash",
                "build_4fastly.sh",
                os.getenv("SERVICE_ID"),
                bitcodes_folder
            ]#,stderr=sys.stdout,
            ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        out, err = p.communicate()

        print(out.decode(), err.decode())
        # check file size
        wasmSize = len(open("multivariant.wasm", 'rb').read())
        try:
            metadata = process_wasm_stats("multivariant.wasm")
        except:
            metadata = { }
        if save_as:
            shutil.copy("multivariant.wasm", f"out/{save_as}")
    except Exception as e:
        print(e)

    return wasmSize, metadata, out

def execute_to_time(service_name, times=50000):

    result = []
    dispatchers = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
        'Cache-Control': 'private, max-age=0, no-cache',
        'Connection': 'keep-alive',
        'Host': 'totally-devoted-krill.edgecompute.app',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    print("Getting execution time distribution")
    for t in range(times):
        try:
            response = requests.get(service_name,headers)
            if 'xtime' in response.headers:
                print(t, response.headers['xtime'])
                result.append(int(response.headers["xtime"]) if 'xtime' in response.headers else -1)
            if 'xdispatcher' in response.headers:
                # print(response.headers['xdispatcher'])
                dispatchers.append(eval(response.headers["xdispatcher"]) if 'xtime' in response.headers else [])
            
        except KeyboardInterrupt:
            break

    return result, dispatchers

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
                        print(content)
                        path = eval(response.headers["xpath"]) if 'xpath' in response.headers else []
                        print(len(path))
                        time = response.headers['xtime']
                        if popl not in results:
                            results[popl] = []
                        results[popl].append({
                            'content': content,
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

def test_with_template(case, template_name, extract_paths=True, extract_times=True, bitcodes_folder="inlined/instrumented", t=1):
    mname, module, usage, entry4Path, entry4time,importNoDiversification, entryNoDiversification, _   = case

    MAIN_TEMPLATE = open(f"templates/{template_name}", 'r').read()

    # To avoid colissions
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("{", "{{")
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("}", "}}")

    # Custom delimiters
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("<%", "{")
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("%>", "}")

    # Now format

    # test entry path
    rPathMain = MAIN_TEMPLATE.format(module=module, usage=usage, entry=entry4Path)

    rPathSize, meta, secmeta = deploy(rPathMain, bitcodes_folder, save_as=f"{mname}_d.wasm" if extract_paths else f"{mname}_paths.wasm", save_sec_as=f"{mname}{extract_paths}{extract_times}{bitcodes_folder}.sec.txt")

    print("rPath size", rPathSize)
    times = execute_to_time("https://totally-devoted-krill.edgecompute.app", times=50000) if extract_times and TEST else { }
    paths = execute_paths("totally-devoted-krill.edgecompute.app", t=t) if extract_paths and TEST else []

    return dict(
        paths=paths,
        times=times,
        packageSize=rPathSize,
        meta = meta
    )

def test_with_instrumentation(case, template="main.rs", times=1):
    return test_with_template(case, template, extract_times=False, bitcodes_folder="inlined/instrumented", t=times)

def test_without_instrumentation(case, template="main_4_time.rs"):
    mname, module, usage, entry4Path, entry4time, importNoDiversification, entryNoDiversification, module  = case
    return test_with_template(case, template, extract_times=True, extract_paths=False, bitcodes_folder=module)

def test_no_diversification(case):
    mname, module, usage, entry4Path, entry4time, importNoDiversification, entryNoDiversification, module  = case

    MAIN_TEMPLATE = open(f"templates/main_single.rs", 'r').read()

    # To avoid colissions
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("{", "{{")
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("}", "}}")

    # Custom delimiters
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("<%", "{")
    MAIN_TEMPLATE = MAIN_TEMPLATE.replace("%>", "}")

    # Now format

    # test entry path
    rPathMain = MAIN_TEMPLATE.format(usage=importNoDiversification,
                                     entry=entryNoDiversification)

    rPathSize, meta, secmeta = deploy(rPathMain, "original", save_as=f"{mname}_original.wasm", save_sec_as=f"{mname}.regular.sec.txt")
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
    print("testing", case[0])

    # pureley random
    print("Random dispatcher")
    # instrumentedPureRandom = test_with_instrumentation(case, template="main_rnd_path.rs", times=1)
    pureRandom = test_without_instrumentation(case, template="main_rnd.rs")
    # pureRandomLocal = test_without_instrumentation(case, template="main_local.rs")


    print("Instrumented diversifier deterministic ")
    # instrumentedDeterministicResults = test_with_instrumentation(case, template="main_deterministic_discriminator_path.rs", times=2)
    print("Original libsodium")
    # noDivResults = test_no_diversification(case) # template f"templates/main_single.rs"
    
    print("Non instrumented diversifier deterministic")
    # nonInstrumentedDeterministicResults = test_without_instrumentation(case, template="main_deterministic_discriminator.rs")
    print("Instrumented diversifier based on hashing")
    # instrumentedResults = test_with_instrumentation(case, times=2)
    print("Diversifier based on hashing")
    # nonInstrumentedResults = test_without_instrumentation(case)


    return None, None, None, None, None, None, pureRandom

def test_all():
    
    cases = [

        bin2base64,
        crypto_aead_chacha20poly1305_ietf_encrypt_detached,
        crypto_aead_chacha20poly1305_ietf_decrypt_detached,
        crypto_core_ed25519_scalar_invert,
        crypto_core_ed25519_scalar_complement,
        crypto_core_ed25519_scalar_random
    ]

    OVERALL = dict()
    
    for case in cases:
        try:
            # Compile all and generate the Wasm files first

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