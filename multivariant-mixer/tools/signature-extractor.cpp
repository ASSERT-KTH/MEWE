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
using namespace crow_linker;

unsigned DebugLevel;


static cl::opt<std::string> InputFilename(cl::Positional, cl::desc("<original bitcode>"), cl::init("-"));

static cl::opt<std::string> FuncName("funcname",
                                      cl::desc("Function name of the function to get the signature")
        , cl::init("allocate_memory"));

int main(int argc, const char **argv) {
    cl::ParseCommandLineOptions(argc, argv);

    LLVMContext context;
    SMDiagnostic error;

    auto bitcode = parseIRFile(InputFilename, error, context);

    for(auto &F: *bitcode){
        if(F.getName().compare(FuncName) == 0){
            //errs() << ";Found " << F.getName() << "\n";

            outs() << "{";
            outs() << "\"rtpe\":" << "\"";
            outs () << *F.getReturnType();
            outs() << "\",\n";

            // argument types
            outs() << "\"args\":" << "[";

            int count = F.arg_size();
            for(auto &arg: F.args()){
                outs() << "{\"isPtr\":" <<  (arg.getType()->isPointerTy()? "true": "false")
                << ",\"tpe\":\"" << *arg.getType() << "\"" << "}";

                count--;
                if(count != 0)
                    outs() << ",";
            }

            outs() << "]\n";
            outs() << "}";
        }
    }

    return 0;
}
