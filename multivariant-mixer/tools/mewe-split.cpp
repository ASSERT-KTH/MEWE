// Copyright 2014 The Souper Authors. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "llvm/ADT/Twine.h"
#include "llvm/IR/LLVMContext.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/Path.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/Signals.h"
#include <system_error>
#include "llvm/Linker/Linker.h"
#include <llvm/IRReader/IRReader.h>
#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/Transforms/Utils/ValueMapper.h"
#include "llvm/Transforms/Utils/Cloning.h"
#include "instrumentor/Instrumentor.h"
#include "discriminator/Discriminator.h"


using namespace llvm;
using namespace mewe_linker;

unsigned DebugLevel;


static cl::opt<std::string> InputFilename(cl::Positional, cl::desc("<original bitcode>"), cl::init("-"));
static cl::opt<std::string> OutFileName(cl::Positional, cl::desc("<result folder>"));

int main(int argc, const char **argv) {
    cl::ParseCommandLineOptions(argc, argv);

    LLVMContext context;
    SMDiagnostic error;

    int count = 1;
    auto bitcode = parseIRFile(InputFilename, error, context);
    for(auto &F: *bitcode){
        errs() << F.getName().str() << "\n";
        if(!F.isDeclaration()) {
            F.replaceAllUsesWith(UndefValue::get(F.getType()));
            // F.eraseFromParent();
        }   
    }

    std::error_code EC;
    llvm::raw_fd_ostream OS(OutFileName + "/b", EC);
    WriteBitcodeToFile(*bitcode, OS);


    OS.flush();

    return 0;
}
