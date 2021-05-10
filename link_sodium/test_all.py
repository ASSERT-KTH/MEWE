import sys
import os
import string
import shutil
from subprocess import check_output
import subprocess
import requests
import json

import urllib3
from cases import *
from extract_wasm_stats import process as process_wasm_stats

urllib3.disable_warnings()

def deploy(mainContent, bitcodes_folder="../sodium4", save_as=None):
    print("Deploying")

    open("src/main.rs", 'w').write(mainContent)
    # executing deploy script
    FNULL = open(os.devnull, 'w')

    out = check_output(
        [
            "bash",
            "build_me.sh",
            os.getenv("SERVICE_ID"),
            bitcodes_folder
        ]#, stderr=subprocess.STDOUT
    )

    # check file size
    wasmSize = len(open("multivariant.wasm", 'rb').read())
    metadata = process_wasm_stats("multivariant.wasm")

    if save_as:
        shutil.copy("multivariant.wasm", f"out/{save_as}")

    return wasmSize, metadata

def execute_to_time(service_name, times=100):

    result = []
    print("Getting execution time distribution")
    for t in range(times):
        response = requests.get(service_name)
        result.append(int(response.headers["xtime"]))
        print(response.headers)

    return result


cache = {

}

BLACKLIST = ["mxp"]

def execute_paths(service_name):
    global cache

    print("Getting execution paths")
    POPS = json.loads(open(f"{sys.argv[1]}/pops.json", 'r').read())
    results = {

    }
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
                    response = requests.get(
                        f"https://cache-{popl}{pcNumber}.hosts.secretcdn.net",
                        headers={
                            'Host': service_name
                        },
                        verify=False,
                        timeout=20
                    )
                    content = response.text
                    print(response.headers)
                    path = response.headers["xpath"].split(",") if 'xpath' in response.headers else []
                    time = response.headers['xtime']
                    results[popl] = {
                        'content': content,
                        'path': path,
                        'time': time
                    }
                    print("Gotcha", popl, pcNumber)
                    cache[popl] = pcNumber
                    break
                except KeyboardInterrupt:
                    return results
                except Exception as e:
                    print(e)
                    if popl in cache and pcNumber == cache[popl]:
                        del cache[popl]

    return results

def test_with_template(case, template_name, extract_paths=True, extract_times=True, bitcodes_folder="../sodium4"):
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

    rPathSize, meta = deploy(rPathMain, bitcodes_folder, save_as=f"{mname}_n1.wasm" if extract_paths else f"{mname}_paths.wasm")

    print("rPath size", rPathSize)
    times = execute_to_time("https://totally-devoted-krill.edgecompute.app") if extract_times else { }
    paths = execute_paths("totally-devoted-krill.edgecompute.app") if extract_paths else []

    return dict(
        paths=paths,
        times=times,
        packageSize=rPathSize,
        meta = meta
    )

def test_with_instrumentation(case, template="main.rs"):
    return test_with_template(case, template, extract_times=False)

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

    rPathSize, meta = deploy(rPathMain, "../sodium5", save_as=f"{mname}_original.wasm")

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
    print("No div")
    noDivResults = test_no_diversification(case)
    print("instrumented deterministic ")
    instrumentedDeterministicResults = test_with_instrumentation(case, template="main_deterministic_discriminator_path.rs")
    print("N1 deterministic")
    nonInstrumentedDeterministicResults = test_without_instrumentation(case, template="main_deterministic_discriminator.rs")
    print("instrumented")
    instrumentedResults = test_with_instrumentation(case)
    print("N1")
    nonInstrumentedResults = test_without_instrumentation(case)

    return noDivResults, instrumentedResults, nonInstrumentedResults, instrumentedDeterministicResults, nonInstrumentedDeterministicResults

def test_all():
    
    cases = [
        crypto_aead_chacha20poly1305_ietf_encrypt_detached,
        crypto_aead_chacha20poly1305_ietf_decrypt_detached,
        crypto_core_ed25519_scalar_invert,
        crypto_core_ed25519_scalar_complement,
        crypto_core_ed25519_scalar_random,
        sodium_increment,
        sodium_memcpy,
        sodium_is_zero,
        sodium_add,
        bin2base64
    ]

    OVERALL = dict()
    for case in cases:
        original, instrumented, nonInstrumented, instrumentedDeterministic, nonInstrumentedDeterministic = test_case(case)

        OVERALL[case[0]] = dict(
            original=original,
            instrumented=instrumented,
            nonInstrumented=nonInstrumented,
            instrumentedDeterministic=instrumentedDeterministic,
            nonInstrumentedDeterministic=nonInstrumentedDeterministic
        )

        print(original["packageSize"], instrumented["packageSize"], nonInstrumented["packageSize"])

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