"""MEWE for rust carg like projects

   Run inside the cargo project
"""
import json
import sys
import subprocess
import os
import shutil
import re
import argparse
import time
from download import download_mewe_binaries
import signal

__keepfiles__ = True
__debugprocess__ = True
__mainreplacename__ = "main2"
__internalmainnamereplace__ = "internal_main"
__skipgeneration__ = False

class BinariesRouter:

    def __init__(self, mewelinkergetter = None, fixergetter = None, 
            version=13):
        self.mewelinkergetter = mewelinkergetter
        self.fixergetter = fixergetter

    def get_mewelinker(self):
        if self.mewelinkergetter is None:
            linker = os.environ.get("MEWELINKER", "")
        else:
            linker = self.mewelinkergetter()

        if __debugprocess__:
            print(linker)
        if not os.path.exists(linker):
            print("Linker binary does not exist.\n Set the env var MEWELINKER or run mewerustc --download-binaries true")
            exit(1)

        return linker

    
    def get_dockerbin(self):
        bin_ = os.environ.get("DOCKER", "docker")
      
        if __debugprocess__:
            print(bin_)

        return bin_

    def get_fixer(self):
        if self.fixergetter is None:
            linker = os.environ.get("MEWEFIXER", "")
        else:
           linker = self.fixergetter()

        if __debugprocess__:
            print(linker)

        if not os.path.exists(linker):
            print("Fixer binary does not exist.\n Set the env var MEWEFIXER or run mewerustc --download-binaries true")
            exit(1)

        return linker

    def run_to_check(self):
        print("Checking binaries...")
        self.get_mewelinker()
        self.get_fixer()

        self.get_dockerbin()
        # TODO, check here the availability of the other binaries, such as docker


class MEWE:


    def __init__(self, router, target, include_files=[], template="main.rs", exploration_timeout_crow = 1, generation_timeout=300):
        self.target = target
        self.template = template
        self.router = router
        self.include_files = include_files
        self.generation_timeout = generation_timeout
        self.exploration_timeout_crow = exploration_timeout_crow

    def run(self):
        if not __keepfiles__:
            if os.path.exists("mewe_out"):
                os.rmdir("mewe_out")

        if not os.path.exists("mewe_out"):
            os.mkdir("mewe_out")
        


        self.clean_project()

        self.compile_project_and_collect_bc()

    def clean_project(self):
        if os.path.exists("target"):
            shutil.rmtree("target")

    def diversify(self, bitcode_file):

        CWD = os.getcwd()
        print(CWD)
        name = f"CROW-worker{time.time()}"
        args = [
            # Use the default linker if not
            self.router.get_dockerbin(),
            "run","-it","--rm","-e", "REDIS_PASS=''","-e", "BROKER_USER='guest'","-e", "BROKER_PASS='guest'",
            "-v", f"{CWD}/mewe_out/crow_out:/slumps/crow/crow/storage/out",
            "-v", f"{CWD}/mewe_out/:/workdir",
            "--entrypoint=/bin/bash",
            "-p",
            "8080:15672",
            f"--name={name}",
            "slumps/crow2:standalone",
            "launch_standalone_bitcode.sh",
            f"/workdir/{os.path.basename(bitcode_file)}",
            f'%DEFAULT.order',
            os.environ.get("CROW_ORDER", "1,2,4,5,5,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21"),
            "%DEFAULT.workers",
            os.environ.get("CROW_WORKERS", "3"),
            "%souper.workers",
            os.environ.get("SOUPER_WORKERS", "2"),
            "%DEFAULT.keep-wasm-files",
            "False",
            "%DEFAULT.exploration-timeout",
            f"{self.exploration_timeout_crow}",
            "%souper.souper-debug-level",
            "1",
            *os.environ.get("CROW_EXTRA_ARGS", "").split(" ")
            ]
        if __debugprocess__:
            print(" ".join(args))

        if not __skipgeneration__:
            if self.exploration_timeout_crow >= 0:
                try:
                    popen = subprocess.Popen(args)    

                    time.sleep(self.exploration_timeout_crow*7 + self.generation_timeout)
                    print("Killing process")
                except KeyboardInterrupt:
                    pass

                popen.terminate()

                subprocess.check_output([
                    "docker",
                    "rm",
                    name,
                    "--force"
                ])

                stdout, err = popen.communicate()
                # the generation + system initialization
                popen.wait()
            else:
                print("Notice that the timeout is lower than zero, meaning that no diversification will be generated with CROW")
        # Collect the variants bitcodes
        variants = []
        for root, _, files in os.walk(f"mewe_out/crow_out"):
            if root.endswith("variants") and "_" in root:
                if len(files) > 0:
                    variants += [ f"{root}/{f}" for f in files if f.endswith(".bc")]

        if len(variants) > 0:
            print(f"CROW generated {len(variants)} variants")
            return variants
        else:
            return [bitcode_file]

    def link_variants(self, original, variants):
        print("Linking variants")

        out = f"{original}.multivariant.bc"
        out_instrumented = f"{original}.multivariant.i.bc"

        linker_args = [
            "--override","--complete-replace=false","-merge-function-switch-cases", "--replace-all-calls-by-the-discriminator", "-mewe-merge-debug-level=2", "-mewe-merge-skip-on-error"
        ]
        args = [
            self.router.get_mewelinker(),
            original,
            out,
            *linker_args,
            f"-mewe-merge-bitcodes=\"{','.join(variants)}\""
        ]
        popen = subprocess.Popen(args, stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)        

        stdout, err = popen.communicate()
        popen.wait()

        if popen.returncode != 0:
            print("Error creating multivariant. Reproduce with")
            print("\t ", " ".join(args))
            print(err.decode())
            exit(1)


        print(stdout.decode())

        popen = subprocess.Popen([
            # Use the default linker if not
            self.router.get_mewelinker(),
            original,
            out_instrumented,
            *linker_args,
            "--instrument-function",
            f"-mewe-merge-bitcodes=\"{','.join(variants)}\""
            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)        

        stdout, err = popen.communicate()

        if popen.returncode != 0:
            print("Error creating multivariant instrumented")
            print(err.decode())
            exit(1)
        print(stdout.decode())
        popen.wait()

        # exit(1)
        if __debugprocess__:
            MEWE.generate_ll(out)
            MEWE.generate_ll(out_instrumented)

        return out, out_instrumented

    def tamper_entrypoint(self, mutivariant_bitcodefile):
        print("Tampering entrypoint of the multivariant_bitcode")

        popen = subprocess.Popen([
            # Use the default linker if not
            self.router.get_fixer(),
            mutivariant_bitcodefile,
            f"{mutivariant_bitcodefile}.rename.bc",
            f'--funcname',
            "main",
            "--replace",
            __mainreplacename__
            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)        

        stdout, err = popen.communicate()
        popen.wait()

        if popen.returncode != 0:
            print("Error")
            print(err.decode())
            print(stdout.decode())
            exit(1)

        # We need the LL IR to get the main4main internal function
        MEWE.generate_ll(f"{mutivariant_bitcodefile}.rename.bc")
        LLCONTENT = open(f"{mutivariant_bitcodefile}.rename.bc.ll",'r').read()


        main4main = re.compile(r"@([_a-zA-Z0-9]+main4main[_a-zA-Z0-9]+)\(")

        g = main4main.findall(LLCONTENT)
        if len(g) == 0:
            print("Internal name not found !")
            exit(1)

        print(g)
        __internalmainname__ = g[0]
        popen = subprocess.Popen([
            # Use the default linker if not
            self.router.get_fixer(),
            f"{mutivariant_bitcodefile}.rename.bc",
            f"{mutivariant_bitcodefile}.fix.bc",
            f'--funcname',
            __internalmainname__,
            "--replace",
            __internalmainnamereplace__
            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)        

        stdout, err = popen.communicate()
        popen.wait()
        if popen.returncode != 0:
            print("Error")
            print(err.decode())
            exit(1)

        # TODO, ideally this fix should come from the LLVM tool itself
        # This is a patch, we convert to LL and we remove the "internal" attribte from the function signature
        MEWE.generate_ll(f"{mutivariant_bitcodefile}.fix.bc",)
        LLCONTENT = open(f"{mutivariant_bitcodefile}.fix.bc.ll", 'r').read()
        LLCONTENT = LLCONTENT.replace(f"internal void @{__internalmainnamereplace__}", f"void @{__internalmainnamereplace__}")
        open(f"{mutivariant_bitcodefile}.fix.bc.ll", 'w').write(LLCONTENT)
        popen_llvm_as = subprocess.Popen([
            # Use the default linker if not
            os.environ.get("LLVMAS", "llvm-as"),
            f"{mutivariant_bitcodefile}.fix.bc.ll",
            f"-o",
            f"{mutivariant_bitcodefile}.fix.bc"
            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)        

        stdout, err = popen_llvm_as.communicate()
        popen_llvm_as.wait()
        if popen_llvm_as.returncode != 0:
            print("Error")
            print(err.decode())
            exit(1)

        if __debugprocess__:
            # Creating the ll
            MEWE.generate_ll(f"{mutivariant_bitcodefile}.fix.bc")
        # return the bitcode path and the name of the internal_main
        return f"{mutivariant_bitcodefile}.fix.bc", __internalmainnamereplace__

    def create_missing_deps_by_using_rustc(self, mainname, mindep):
        
        print(f"Loading template 'templates/{self.template}'")

        ABS_PATH = os.path.join(os.path.dirname(__file__),) 
        
        if os.path.exists(f"mewe_out/{self.template}"):
            shutil.rmtree(f"mewe_out/{self.template}")

        shutil.copytree(f"{ABS_PATH}/templates/{self.template}", f"mewe_out/{self.template}")

        content = open(f"mewe_out/{self.template}/src/bin/main.rs", 'r').read()
        
        content = content.replace("{{name}}", mainname)

        open(f"mewe_out/{self.template}/src/bin/main.rs", 'w').write(content)


        print("Calling rustc")
        CWD = os.getcwd()

        os.environ['RUSTFLAGS'] = f"-C link-arg={CWD}/{mindep}"
        popen = subprocess.Popen([
            "cargo",
            "build",
            "--release",
            f"--target={self.target}",
            ], cwd=f"mewe_out/{self.template}",stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)  
        stdout, err = popen.communicate()

        stdout = popen.wait()

        if popen.returncode != 0:
            print(err.decode())
            exit(1)

    @staticmethod
    def generate_ll(bitcodefile):
        popen_ll = subprocess.Popen([
            # Use the default linker if not
            os.environ.get('LLVMDIS', 'llvm-dis'),
            bitcodefile,
            '-o',
            f'{bitcodefile}.ll'
                        ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)

        stdout, err = popen_ll.communicate()
        popen_ll.wait()

    def link_bitcodes(self, bitcodes):
        print("Linking bitcodes")

        if __debugprocess__:
            print(bitcodes)
        
        print("Print calling linker at '$LINKER'")
        popen = subprocess.Popen([
            # Use the default linker if not
            os.environ.get('LINKER', 'llvm-link'),
            *bitcodes,
            '-o',
            f'mewe_out/all.bc'
            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        
        if __debugprocess__:
            # Creating the ll
            MEWE.generate_ll(f'mewe_out/all.bc')
        stdout, err = popen.communicate()
        popen.wait()

        if __debugprocess__:
            print(err.decode())
            
        if popen.returncode != 0:
            print("Error on linking phase !")
            exit(1)
        
        variants = self.diversify("mewe_out/all.bc")

        if len(variants) > 1:
            # Use the LINKER to create the multivariant
            print("Creating multivariant library")
            multivariant_bitcode, multivariant_bitcode_instrumented = self.link_variants("mewe_out/all.bc", variants)
            # Change the tempalte to use the dispatcher
            if "with_dispatcher" not in self.template:
                self.template = "with_dispatcher"
        else:
            print("No variant could be created")
            multivariant_bitcode = "mewe_out/all.bc"

        finalbitcode, name = self.tamper_entrypoint(multivariant_bitcode)

        self.create_missing_deps_by_using_rustc(name, finalbitcode)

        print("Collect your binary in the <template folder>/target !!")

    def compile_project_and_collect_bc(self):
        os.environ['RUSTFLAGS'] = "--emit=llvm-bc"
        popen = subprocess.Popen([
            'cargo',
            'build',
            '--release',
            '--target',
            self.target,

            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        print("Compiling project ...")
        stdout, err = popen.communicate()
        popen.wait()

        if __debugprocess__:
            print(err.decode())

        print("Retrieving llvm bitcodes")

        bitcodes = []

        bitcodes_root_folder = f"target/{self.target}/release/deps"

        if __debugprocess__:
            print("\t","\n\t".join(os.listdir(bitcodes_root_folder)))
        # Adding passed included bitcodes
        for bc in self.include_files:
            bitcodes.append(bc)
            if __debugprocess__:
                shutil.copyfile(bc, f"mewe_out/{os.path.basename(bc)}")

                MEWE.generate_ll(f"mewe_out/{os.path.basename(bc)}")


        for bc in os.listdir(bitcodes_root_folder):
            if bc.endswith(".bc"):
                shutil.copyfile(f"{bitcodes_root_folder}/{bc}", f"mewe_out/{bc}")
                bitcodes.append(f"mewe_out/{bc}")

        self.link_bitcodes(bitcodes)
        #RUSTFLAGS="--emit=llvm-bc  -C linker-plugin-lto=no" cargo build --release --target=$target || exit 1

if __name__ == "__main__":
    print("MEWE !")

    parser = argparse.ArgumentParser(description='MEWE cli tool.')
    parser.add_argument('--target', metavar='x', type=str,      
                        nargs=1, default=["wasm32-wasi"],
                        help='Compilatio target')
    parser.add_argument('--template', metavar='t', type=str,      
                    nargs=1, default=["regular"],
                    help='Entrypoint tampering template')
                                        

    parser.add_argument('--include', metavar='i', type=str,      
                    nargs='+', default=[],
                    help='Bitcodes to include in the linking phase')

    parser.add_argument('--llvm-version', metavar='l', type=int,      
                    nargs=1, default=[13],
                    help='LLVM version to use in the linking')

    parser.add_argument('--download-binaries', metavar='d', type=bool,      
                    nargs=1, default=True,
                    help='Download precompiled binaries o MEWE for this OS and use them instead of the ones provided in the environment variables')

    parser.add_argument('--generation-timeout', type=int,      
                    nargs=1, default=[60],
                    help='Stop CROW after x seconds (default 60)')

    parser.add_argument('--exploration-timeout', type=int,      
                    nargs=1, default=[30],
                    help='Stop CROW exploration after x seconds (default 30)')

    args = parser.parse_args()

    if args.download_binaries:
        print("Downloading binaries")
        paths = download_mewe_binaries()
        bins = paths[args.llvm_version[0]]

        router = BinariesRouter(
            mewelinkergetter = bins['mewe_linker'],
            fixergetter = bins['mewe_fixer'])
    else:
        router = BinariesRouter()
    
    router.run_to_check()

    mewe = MEWE(router, target=args.target[0], 
        template=args.template[0], include_files=args.include, 
        generation_timeout=args.generation_timeout[0],
        exploration_timeout_crow=args.exploration_timeout[0])

    mewe.run()