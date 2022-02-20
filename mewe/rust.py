"""MEWE for rust carg like projects

   Run inside the cargo project
"""
import json
import sys
import subprocess
import os
import shutil
import re

__keepfiles__ = True
__target__ = "wasm32-wasi" # Infer from project here :)
__debugprocess__ = True
__mainreplacename__ = "main2"
__internalmainnamereplace__ = "internal_main"

class MEWE:

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

        print("TODO callling CROW")

        return [bitcode_file]

    def link_variants(self, bitcodes):
        raise Exception("Not implemented")

    def tamper_entrypoint(self, mutivariant_bitcodefile):
        print("Tampering entrypoint of the multivariant_bitcode")

        popen = subprocess.Popen([
            # Use the default linker if not
            os.environ["MEWEFIXER"],
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
            os.environ["MEWEFIXER"],
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
        print("Loading template 'templates/main.rs'")

        content = open(os.path.join(os.path.dirname(__file__), "templates/main.rs"), 'r').read()
        
        content = content.replace("{{name}}", mainname)

        open("mewe_out/main.rs", 'w').write(content)


        print("Calling rustc")

        popen = subprocess.Popen([
            "rustc",
            "-C",
            f"link-arg={mindep}",
            f"--target={__target__}",
            "mewe_out/main.rs",
            ], stderr=subprocess.PIPE,
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
            multivariant_bitcode = self.link_variants(variants)
        else:
            print("No variant could be created")
            multivariant_bitcode = "mewe_out/all.bc"

        finalbitcode, name = self.tamper_entrypoint(multivariant_bitcode)

        self.create_missing_deps_by_using_rustc(name, finalbitcode)

        print("Collect your binary at the root folder !!")

    def compile_project_and_collect_bc(self):
        os.environ['RUSTFLAGS'] = "--emit=llvm-bc"
        popen = subprocess.Popen([
            'cargo',
            'build',
            '--release',
            '--target',
            __target__,

            ], stderr=subprocess.PIPE,
            stdout=subprocess.PIPE)
        print("Compiling project ...")
        stdout, err = popen.communicate()
        popen.wait()

        if __debugprocess__:
            print(err.decode())

        print("Retrieving llvm bitcodes")

        bitcodes = []

        bitcodes_root_folder = f"target/{__target__}/release/deps"

        for bc in os.listdir(bitcodes_root_folder):
            if bc.endswith(".bc"):
                shutil.copyfile(f"{bitcodes_root_folder}/{bc}", f"mewe_out/{bc}")
                bitcodes.append(f"mewe_out/{bc}")

        self.link_bitcodes(bitcodes)
        #RUSTFLAGS="--emit=llvm-bc  -C linker-plugin-lto=no" cargo build --release --target=$target || exit 1

if __name__ == "__main__":
    print("MEWE !")

    mewe = MEWE()
    mewe.run()