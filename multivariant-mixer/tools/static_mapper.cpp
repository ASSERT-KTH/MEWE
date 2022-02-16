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
#include "llvm/Analysis/CFGPrinter.h"
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
#include <fstream>
#include <iostream>

using namespace llvm;
using namespace crow_linker;
using namespace std;

unsigned DebugLevel;


static cl::opt<std::string> InputFilename(cl::Positional, cl::desc("<original bitcode>"), cl::init("-"));

static cl::opt<bool> UseIndirectAsUndefinedNode(
        "use-indirect-as-undefined-node",
        cl::desc("Merge all indirect calls to the same Node"),
        cl::init(false));


static cl::opt<bool> UseIndirectCallsToAllNodes(
        "use-indirect-to-all-nodes",
        cl::desc("The most conservative strategy. Since the indirect call can go to any function, add and edge to all"),
        cl::init(false));


static cl::opt<bool> DoNotUseIndirectCalls(
        "no-indirect-calls",
        cl::desc("Remove indirect call edges"),
        cl::init(true));


static cl::opt<std::string> NodesFile("nodes-file",
                                      cl::desc("Name of the file containing the nodes info")
        , cl::init("nodes.txt"));


static cl::opt<std::string> EdgesFile("edges-file",
                                       cl::desc("Name of the file containing the edges info")
        , cl::init("edges.txt"));

static cl::opt<std::string> ZeroFilteredNodesFile("zero-file",
                                      cl::desc("Name of the file containing the edges info")
        , cl::init("zero.txt"));

static cl::opt<std::string> ZeroFilteredCFGNodesFile("zero-cfg-file",
                                                  cl::desc("Name of the file containing the edges info")
        , cl::init("zero.cfg.txt"));

static cl::opt<std::string> MetaFile("meta-file",
                                       cl::desc("Name of the file containing the metadata info")
        , cl::init("meta.txt"));


static cl::opt<std::string> CFGFile("cfg-file",
                                     cl::desc("CFG file")
        , cl::init("cfg.txt"));

static std::map<std::string, int> OutDegree;
static std::map<std::string, int> OutDegreeCFG;
static std::map<std::string, int> Visited;

int main(int argc, const char **argv) {
    cl::ParseCommandLineOptions(argc, argv);

    LLVMContext context;
    SMDiagnostic error;

    auto bitcode = parseIRFile(InputFilename, error, context);
    ofstream nodes_file;
    nodes_file.open (NodesFile);

    if(UseIndirectAsUndefinedNode)
        nodes_file << "UNDEFINED";
    // First generate the function nodes
    for(auto &F: *bitcode){
        nodes_file << F.getName().str() << "\n";
    }
    nodes_file.close();
    ofstream cfg_file;
    cfg_file.open (CFGFile);

    cfg_file.close();

    ofstream edges_file;
    edges_file.open (EdgesFile);

    int count_of_direct_calls = 0;
    int count_of_indirect_calls = 0;

    // Create the edges for the call graph
    for(auto &F: *bitcode){
        edges_file << F.getName().str() << "\n";
           OutDegree[F.getName().str()] = 0;
        // Call graph
        for(auto &BB: F){
            int index = 0;
            for(auto inst = BB.begin(); inst != BB.end(); ++inst) {
                if(isa<CallInst>(inst)) {
                    auto call = cast<CallInst>(inst);

                    if(call->getCalledFunction()) {
                        edges_file << "->" << call->getCalledFunction()->getName().str() << "\n";
                        count_of_direct_calls++;
                        OutDegree[F.getName().str()]++;
                    }
                    else{

                        count_of_indirect_calls++;
                        if(UseIndirectAsUndefinedNode && !UseIndirectCallsToAllNodes && !DoNotUseIndirectCalls){
                            edges_file << F.getName().str() << ",UNDEFINED" << "\n";
                            continue;
                        }


                        if(!UseIndirectAsUndefinedNode && UseIndirectCallsToAllNodes && !DoNotUseIndirectCalls){
                            // TODO
                            continue;
                        }


                        // !UseIndirectAsUndefinedNode && !UseIndirectCallsToAllNodes && !DoNotUseIndirectCalls => Do nothing

                        //call->dump();
                        auto callvar = call->getCalledOperand();
                        errs() << callvar->getName() << " ";
                        errs() << "It is an indirect call, skipping since the option is to remove indirect calls \n";
                    }
                }
                if(isa<InvokeInst>(inst)) {
                    auto call = cast<InvokeInst>(inst);

                    outs() << "Invoking!!";
                    exit(1);
                    //if(call->getCalledFunction())
                        //outs() << F.getName() << ","  << call->getCalledFunction()->getName() << "\n";
                }
            }
        }
    }
    edges_file.close();

    ofstream meta_file;
    meta_file.open (MetaFile);

    meta_file << "Direct calls: " << count_of_direct_calls << "\n";
    meta_file << "Indirect calls: " << count_of_indirect_calls << "\n";

    meta_file.close();


    ofstream zero_file;
    zero_file.open (ZeroFilteredNodesFile);

    ofstream zero_cfg_file;
    zero_cfg_file.open (ZeroFilteredCFGNodesFile);

    for(auto &k: OutDegree){
        if(k.second == 0)
        {
            zero_file << k.first << "\n";
        }
    }

    for(auto &k: OutDegreeCFG){
        if(k.second == 0)
        {
            zero_cfg_file << k.first << "\n";
        }
    }

    zero_file.close();
    zero_cfg_file.close();

    return 0;
}
