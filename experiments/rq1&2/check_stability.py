import sys
import redis
from multiprocessing import Pool
import subprocess

import json
import os
import time
import platform
import hashlib
import re
import base64 as b64
import functools

from multiprocessing import Pool


MODULE_NAME=re.compile(r"(.*)_(\d+)$")
FUNCTION_NAME=re.compile(r"\n[ \t]+\(func (\$[\w:_\$\.]+) \(type \d\)")
EXPORT_NAME=re.compile(r"\n[ \t]+\(export \"([\w:_\$\.]+)\" \(func")

BLACK_LIST=["$__wasm_call_ctors", "__wasm_call_ctors"]
SAVE_BINS=False
USE_EXPORT=True
GENERATE_WASM_IF_MISSING=True

#
def get_b64andhash(filepath):
    content = open(filepath, 'rb').read()
    coded = b64.encodebytes(content).decode() if SAVE_BINS else ""
    #base64[f] = coded
    hsh = hashlib.sha512(content).hexdigest()
    #hashes[f] = hsh

    return coded, hsh


def get_function_name(program_folder, program, variant):

    result = []
    print(variant)
    REG=EXPORT_NAME if USE_EXPORT else FUNCTION_NAME
    if os.path.exists(f"{program_folder}/{program}/wasm/{variant}.bc.wasm"):
        c = get_wat_content(f"{program_folder}/{program}/wasm/{variant}.bc.wasm") 
        # open(f"{program_folder}/{program}/wat/{variant}.bc.wat", 'r').read()
    else:
        c = get_wat_content(f"{program_folder}/{program}/wasm/{variant}.original.bc.wasm") 
        #open(f"{program_folder}/{program}/wat/{variant}.original.bc.wat", 'r').read()

    for f in REG.findall(c):
        if f not in BLACK_LIST:
            #print(f)
            #exit(0)
            nf = re.sub(r"^\$", "", f) # sanitize
            print(nf)
            result.append(nf)
    print(result)

    if len(result) == 1:
        return result[0]
    return result

def get_single_variant_name(bitcodename, file):
    return file.replace(f"{bitcodename}_", "").replace(".bc", "").replace(".wasm", "")

def get_variants_name(folder, bitcodename, filters=[".bc", ".wasm"], original=""):
    print(original)
    filters.append(f"{bitcodename}_")
    variants = [functools.reduce(lambda p, c: p.replace(c, ""), filters, variant)  for variant in os.listdir(folder) if variant !=  original]
            # split number of applied variants
    variants = [ 
        [v.replace("[", "").replace("]", "") for v in variantname.split("]") if v]
        for variantname in variants
    ]

    return variants

def get_native_code(wasmfile):
    print(wasmfile)
    subprocess.check_output(
        [
            os.environ.get("WASMTIME"),
            "wasm2obj",
            wasmfile,
            f"{wasmfile}.obj",
            '--opt-level',
            "2"
        ]
    )
    code64, hsh = get_b64andhash(f"{wasmfile}.obj")
    
    return code64, hsh

def get_wat_content(wasmfile):
    print(wasmfile)
    o = subprocess.check_output(
        [
            os.environ.get("WASM2WAT"),
            wasmfile
        ]
    )

    return o.decode()

def get_wat(wasmfile):
    print(wasmfile)
    subprocess.check_output(
        [
            os.environ.get("WASM2WAT"),
            wasmfile,
            "-o",
            f"{wasmfile}.wat"
        ]
    )

    return f"{wasmfile}.wat"

def get_diff(wat1, wat2):
    p = subprocess.Popen(
        [
            "diff",
            wat1,
            wat2,
            "-y"
        ], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )

    stdout, err = p.communicate()

    #print(stdout, err)
    return stdout.decode()
def process_bitcode(t):
    allprograms_folder, bitcode_folder, bitcodename = t
    # get original bitcode
    original_bitcode = f"{bitcode_folder}/bitcodes/{bitcodename}.original.bc"
    result = {}
    result['native_hashes'] = []
    result['wasm_hashes'] = []
    result['bitcodename'] = bitcodename
    # generate original wasm

    if not os.path.exists(f"{bitcode_folder}/wasm"):
        os.mkdir(f"{bitcode_folder}/wasm")

    if not os.path.exists(f"{bitcode_folder}/wat"):
        os.mkdir(f"{bitcode_folder}/wat")

    try:
        out = subprocess.check_output([
                os.environ.get("WASMLD"),
                original_bitcode,
                "-o",
                f"{bitcode_folder}/wasm/{bitcodename}.original.bc.wasm",
                "--no-entry",
                "--export-all",
            "--allow-undefined"
            ])
        out = subprocess.check_output([
            os.environ.get("WASMLD"),
            original_bitcode,
            "-o",
            f"{bitcode_folder}/wasm/{bitcodename}.bc.wasm",
            "--no-entry",
            "--export-all",
            "--allow-undefined"
            ])
    except Exception as e:
        print(e)
        return result
    if os.path.exists(original_bitcode):

        # check if it has variants
        bitcode_variants_folder = f"{bitcode_folder}/bitcodes/variants"

        if not os.path.exists(bitcode_variants_folder):
            os.mkdir(bitcode_variants_folder)

        if len(os.listdir(bitcode_variants_folder)):
            print(bitcodename, "has", len(os.listdir(bitcode_variants_folder)), "bitcode variants")

            # TODO get functions name
            function_names = get_function_name(allprograms_folder, bitcodename, bitcodename)
            print(function_names)
            # TODO get original module

            module_name = MODULE_NAME.match(bitcodename).group(1)
            module_name = module_name.replace("sodium8_", "")

            print(module_name)

            result["functions"] = function_names
            result["module_name"] = module_name

            # get bitcode files and code them to base64 for storage

            base64 = {

            }
            hashes = {

            }

            bitcode_variants = os.listdir(bitcode_variants_folder)

            for f in os.listdir(bitcode_variants_folder):
                coded, hsh = get_b64andhash(f"{bitcode_variants_folder}/{f}")
                base64[f] = coded
                hashes[f] = hsh

            # get variants name
            variants = get_variants_name(bitcode_variants_folder, bitcodename)

            result['bitcodes'] = {

            }
            result['bitcodes']["variants"] = variants
            result['bitcodes']["variants_count"] = len(variants)
            result['bitcodes']["hashes"] = hashes
            result['bitcodes']["base64"] = base64
            #print(variants)

            # get wasm variants
            wasm_variants_folder = f"{bitcode_folder}/wasm"

            wasm_variant_files = [w for w in os.listdir(wasm_variants_folder) if w.endswith(".wasm")]

            #if len(wasm_variant_files) < len(bitcode_variants): # the conversion to wasm failed in some cases
            if GENERATE_WASM_IF_MISSING:
                print("Generating missing wasm files", len(bitcode_variants), len(wasm_variant_files), bitcode_variants_folder, wasm_variants_folder)
                for bitcode in bitcode_variants:
                    print("Generating", bitcode)
                    out = subprocess.check_output([
                        os.environ.get("WASMLD"),
                        f"{bitcode_variants_folder}/{bitcode}",
                        "-o",
                        f"{wasm_variants_folder}/{bitcode}.wasm",
                        "--no-entry",
                        "--export-all",
                        "--allow-undefined"
                    ])

            wasm_variant_files = [w for w in os.listdir(wasm_variants_folder) if w.endswith(".wasm")]

            if len(wasm_variant_files) > 1:
                # it has wasm variants, -1, the original
                print(bitcodename, "has",len(wasm_variant_files) -1, "wasm variants" )

                if len(os.listdir(bitcode_variants_folder)) - len(wasm_variant_files) - 1 != 0:
                    print("Some llvm 2 wasm preservation is lost or some cannot be converted to wasm", bitcodename, wasm_variants_folder)


                result['wasm'] = {}
                result['wasm']['variants'] = get_variants_name(wasm_variants_folder, bitcodename, original=f"{bitcodename}.bc.wasm")
                result['wasm']['base64'] = {}
                result['wasm']['variants_count'] = len(result['wasm']['variants'])
                result['wasm']['hashes'] = {}


                result['native'] = {}
                result['native']['base64'] = {}
                result['native']['hashes'] = {}

                result['pairs'] = []

                # saving original also
                if os.path.exists(f"{wasm_variants_folder}/{bitcodename}.bc.wasm"):
                    coded, hsh = get_b64andhash(f"{wasm_variants_folder}/{bitcodename}.bc.wasm")
                else:
                    coded, hsh = get_b64andhash(f"{wasm_variants_folder}/{bitcodename}.original.bc.wasm")
                    
                result['wasm']['original_base4']= coded
                result['wasm']['original_hash'] = hsh

                if os.path.exists(f"{wasm_variants_folder}/{bitcodename}.bc.wasm"):
                    originalb64Native, nativehashOriginal = get_native_code(f"{wasm_variants_folder}/{bitcodename}.bc.wasm")
                else:
                    originalb64Native, nativehashOriginal = get_native_code(f"{wasm_variants_folder}/{bitcodename}.original.bc.wasm")
                if os.path.exists(f"{wasm_variants_folder}/{bitcodename}.bc.wasm"):
                    oname = f"{bitcodename}.bc.wasm"
                else:
                    oname = f"{bitcodename}.original.bc.wasm"


                result['native']['original_hash'] = nativehashOriginal
                result['native']['original_base64'] = originalb64Native
                for wasm in wasm_variant_files + [oname]:
                    
                    coded, hsh = get_b64andhash(f"{wasm_variants_folder}/{wasm}")
                    result['wasm']['base64'][wasm] = coded
                    result['wasm']['hashes'][wasm] = hsh

                    # Do the native transformation to get preservation
                    nativebase64, nativehash = get_native_code(f"{wasm_variants_folder}/{wasm}")

                    result['native']['base64'][wasm] = nativebase64
                    result['native']['hashes'][wasm] = nativehash

                    result['native_hashes'].append(nativehash)
                    result['wasm_hashes'].append(hsh)

                    # Aggregate data for better later comparison
                    result['pairs'].append([

                        dict(
                            wasm_hash = hsh,
                            native_hash = nativehash,
                            variant_name = get_single_variant_name(bitcodename, wasm),
                            function_name = function_names,
                            diff = get_diff(
                                get_wat(f"{wasm_variants_folder}/{oname}"),
                                get_wat(f"{wasm_variants_folder}/{wasm}")
                            ),
                            isPreserved = nativehash != nativehashOriginal
                            # TODO add souper replacement here for later comparison
                        ),
                        dict(

                        # original second,
                            wasm_hash = result['wasm']['original_hash'],
                            native_hash = nativehashOriginal,
                            variant_name = "original",
                            function_name = function_names
                        )]
                    )

                #print(result['wasm'])


    # print(result)
    return result
def process(folder):
    

    with Pool(10) as p:
        rs = p.map(process_bitcode, [(folder, f"{folder}/{f}", f) for f in
            os.listdir(folder)
        ])

        OVERALL = dict(
            zip(
                [r['bitcodename'] for r in rs],
                rs
            )
        )

        open(f"rq1&2/results/{sys.argv[2]}/rq11_{sys.argv[2]}_.stability.json", 'w').write(json.dumps(OVERALL, indent=4))


if __name__ == "__main__":

    programsFolder = sys.argv[1]

    process(programsFolder)

