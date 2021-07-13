import sys
import os
import json
import subprocess
import re
import hashlib

DEBUG = True

def extract_symbol(bitcodefile, name):
    tmpbin = subprocess.check_output(
        [
            "llvm-extract",
            bitcodefile,
            f"--func={name}",
            "-o",
            "tmp.bc"
        ]
    )

    out = subprocess.check_output(
        [
            "llvm-dis",
            "tmp.bc",
            '-o',
            "-"
        ]
    )

    out = out.decode()

    # extract only the llvm function
    content = ""
    signature = ""
    #print(name, out)

    OPEN=False
    for l in out.split("\n"):
        if l.startswith("define"):
            if f"@{name}" in l:
                #content += f"{l}\n"
                signature = l
                print(l)
                OPEN=True
                continue
        if l == '}':
            OPEN = False
            #content += f"{l}\n"
            continue
        if OPEN:
            content += f"{l}\n"


    #print(content)
    return content, signature

def get_functions(bitcode):
    out = subprocess.check_output(
        [
            "llvm-nm",
            bitcodefile
        ]
    )

    out = out.decode()

    result = {

    }

    funcnamere = re.compile(r"(.*?)(_\d+_|\.\d+|_original)$")

    for f in out.split('\n'):

        if f:
            sanitized = f
            sanitized = sanitized.replace("-------- ", "")
            sanitized = sanitized.strip()
            
            symbols = sanitized.split(" ")

            attr, name = symbols
            name = name.strip()

            if attr.lower() not in ['t']:
                continue

            m = funcnamere.match(name)
            
            r = {

            }

            if m:
                base = m.group(1)
                meta = [m.group(2)]
            else:
                base = name
                meta = []
            
            r['base'] = base
            r['attr'] = attr
            r['name'] = name
            r['meta'] = meta
            r['raw'] = f

            # get llvm rep of the symbol

            llvmcode, signature = extract_symbol(bitcodefile, name)

            if "discriminate" in llvmcode:
                meta.append('dispatcher')

            r['llvmir'] = llvmcode
            r['llvm_signature'] = signature
            r['llvmhash'] = hashlib.sha512(llvmcode.encode()).hexdigest()

            if base not in result:
                result[base] = {
                    'variants': []
                }
            
            print("Variant for ", base, name)
            result[base]['variants'].append(r)
    

    # Calculate general stats per group
    for k in result:
        cumul = set()
        for func in result[k]['variants']:
            hsh = func['llvmhash']
            cumul.add(hsh)

            if DEBUG:
                print(func["name"], func["meta"])
                print(func["llvmir"])
                print("=======")
                print()
        
        result[k]['unique_llvm'] = len(cumul)
        result[k]['variants_count'] = len(result[k]['variants'])

        if len(cumul) != len(result[k]['variants']):
            sys.stderr.write(f"{k} {len(result[k]['variants'])} {len(cumul)}\n")
        
    if DEBUG:
        for k in result:
            print(k, len(result[k]))

    return result


# parsing re
def generate_function_import(bitcodefile, name):

    def map_tpe(llvm_tpe):

        if llvm_tpe == "i8*":
            return "*mut libc::c_char"

        if llvm_tpe == "i64*":
            return "*mut i64"

        if llvm_tpe == "i32*":
            return "*mut i32"

        if llvm_tpe == "void":
            return "()"

        return llvm_tpe

    abspath = os.path.abspath(bitcodefile)
    print(abspath, name)
    name = name.strip()

    out = subprocess.check_output(
        [
            os.environ.get("SIGNATURE_EXTRACTOR"),
            abspath,
            f'-funcname={name}'
        ], stderr=sys.stderr
    )

    out = out.decode()
    out = json.loads(out)

    print(out)

    content = ""
    content += "extern \"C\" {\n"
    content += f"\tpub fn {name}("

    for i,a in enumerate(out["args"]):
        content += f'l{i}: {map_tpe(a["tpe"])}'
        if i < len(out['args']) - 1:
            content += ","

    content += ") -> "
    content += map_tpe(out["rtpe"])
    content += ";\n}\n"

    return content

def calculate_preservation(bitcodefile, functions, do_diff=True):
    
    def get_function_body(start_at, content):
        r = ""

        OPEN = 0

        for c in content[start_at:]:
            if c == '(':
                OPEN += 1
            if c == ')':
                OPEN -= 1
            r += c

            if OPEN == 0:
                break

            

        return r

    for k in functions:
        data = functions[k]
        if data["unique_llvm"] - 1 > 1: # number of variants should be more than 1 plus the dispatcher

            first_instance = data['variants'][0]
            llvm_signature = first_instance['llvm_signature']

            print(k, data['unique_llvm'], llvm_signature)

            if "internal" in llvm_signature or "hidden" in llvm_signature:
                continue

            fname = first_instance['name']
            rs_export = generate_function_import(bitcodefile, fname)

            # create rust template and compile using the most preservative flags

            # load template
            t = open("template.rs", "r").read()

            nc = t.format(
                external=rs_export,
                name=k
            )
            open("src/main.rs", "w").write(nc)

            env = dict(
                os.environ,
                # example export /Users/javierca/Documents/Develop/slumps/souper/third_party/llvm-Release-install/bin/clang"
                RUSTFLAGS=f"-C link-args=--sysroot={os.environ.get('SYSROOT')} -C link-arg={bitcodefile} -C opt-level=0 -C lto=off -C inline-threshold=0 -C  link-dead-code -C target-feature=-crt-static -C linker={os.environ.get('WASMLD')} "
            )
            # inject autogenerated
            out = subprocess.check_output(
                [
                    "cargo",
                    "build",
                    "--target=wasm32-wasi",
                    "--release"
                    ],
                    env=env
            )

            out = subprocess.check_output(
                [
                    os.environ.get("WASM2WAT"),
                    "target/wasm32-wasi/release/template.wasm",
                    
                ]
            )

            out = out.decode()

            # sanitize external imports

            if '(import "env"' in out:
                continue
            

            # parse and get function on the wat file

            for v in data['variants']:
                if 'dispatcher' not in v['meta']:
                    # find this function inside the wasm module
                    i = out.index(f"(func ${v['name']}")
                    
                    if i:
                        wasmfunction = get_function_body(i, out)
                        # replace name by original
                        wasmfunction = wasmfunction.replace(v['name'], k)
                        v['wasmbody'] = wasmfunction
                        v['wasmhash'] = hashlib.sha256(wasmfunction.encode()).hexdigest()

            # Calculate general stats per group
    FUNCTIONS_COUNT = 0
    PAIRS_COUNT = 0
    for k in functions:
        if any([ 'wasmhash' in v for v in functions[k]['variants'] ]):
            cumul = set()
            for func in functions[k]['variants']:
                if 'wasmhash' in func:
                    hsh = func['wasmhash']
                    cumul.add(hsh)
                    print

            
                    if DEBUG:
                        print(func["name"], func["meta"])
                        print(func["wasmbody"])
                        print("=======")
                        print()

                        open(f"out/{func['name']}.wat", 'w').write(func["wasmbody"])

            functions[k]['unique_wasm'] = len(cumul)
            functions[k]['variants_wasm_count'] = len(functions[k]['variants'])
            functions[k]['wasm_pairs'] = functions[k]['variants_wasm_count']*(functions[k]['variants_wasm_count'] - 1)/2
            FUNCTIONS_COUNT += 1 if len(functions[k]['variants']) > 1 else 0
            PAIRS_COUNT += functions[k]['wasm_pairs']

            if len(cumul) != len(functions[k]['variants']) - 1:
                sys.stderr.write(f"{k} {len(functions[k]['variants'])} {len(cumul)}\n")
    
    print(FUNCTIONS_COUNT, PAIRS_COUNT)

if __name__ == "__main__":
    bitcodefile = sys.argv[1]

    # get functions
    if sys.argv[2] == "llvm":
        functions = get_functions(bitcodefile)
        open("functions.json", 'w').write(json.dumps(functions, indent=4))
    elif sys.argv[3] == "wasm":
        functions = json.loads(open(sys.argv[1], 'r').read())
        result = calculate_preservation(sys.argv[2], functions)

        open("functions.p.wasm.json", 'w').write(json.dumps(functions, indent=4))

        