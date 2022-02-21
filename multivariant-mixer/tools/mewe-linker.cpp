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
#include <future>
#include "llvm/Bitcode/BitcodeWriter.h"
#include "llvm/Transforms/Utils/ValueMapper.h"
#include "llvm/Transforms/Utils/Cloning.h"

#include "common/Common.h"
#include "instrumentor/Instrumentor.h"
#include "discriminator/Discriminator.h"


using namespace llvm;
using namespace mewe_linker;

unsigned DebugLevel;

/* Discrminator options and flags */
extern std::string MergeFunctionSuffix;
extern std::string DiscrminatorCallbackName;
extern bool MergeFunctionAsPtr;
extern bool MergeFunctionAsSCases;

/* Instrumentor options */
extern bool InstrumentFunction;
extern bool InstrumentBB;
extern bool NoInline;
extern bool AggressiveNoInline;

static cl::opt<std::string> InputFilename(cl::Positional, cl::desc("<original bitcode>"), cl::init("-"));

static cl::opt<std::string> OutFileName(cl::Positional, cl::desc("<result bitcode>"));

static cl::list<std::string> BCFiles("mewe-merge-bitcodes",
                                     cl::desc("<variant file>")
        , cl::OneOrMore, cl::CommaSeparated);


static cl::list<std::string> FunctionNames("mewe-merge-functions",
                                           cl::desc("<function name>"),
         cl::CommaSeparated);

static cl::opt<std::string> FuncSufix("mewe-merge-func-sufix",
                                      cl::desc("Name sufix in the added functions")
        , cl::init("_"));

static cl::opt<bool> SkipOnError(
        "mewe-merge-skip-on-error",
        cl::desc("Skip the merge of a module if error"),
        cl::init(true));


static cl::opt<bool> NotLookForFunctions(
        "skip-function-names",
        cl::desc("Skip function names"),
        cl::init(false));


static cl::opt<bool>
        Override("override", cl::desc("Override symbols"), cl::init(false));

static cl::opt<bool>
        InjectOnlyIfDifferent("merge-only-if-different", cl::desc("Add new function only if it is different to the original one"), cl::init(true));

static cl::opt<bool>
        CompleteReplace("complete-replace", cl::desc("Replace by incoming function if signature match"), cl::init(false));

static cl::opt<unsigned, true> DebugLevelFlag(
        "mewe-merge-debug-level",
        cl::desc("Pass devbug level, 0 for none"),
        cl::location(DebugLevel),
        cl::init(0));

static unsigned modulesCount = 0;


static void deinternalize_module(Module &M, bool saveBackup=false){
    // For functions
    for(auto &F: M){
        if(saveBackup) {
            backupLinkage4Functions[F.getName().str()] = F.getLinkage();

            if (DebugLevel > 3)
                errs() << "Saving linkage for " << F.getName() << "\n";

            std::string originalName;
            llvm::raw_string_ostream originalNameOutput(originalName);
            originalNameOutput << F.getName().str() << "_original";
            // Ok, saving original just in case
            backupLinkage4Functions[originalName] = F.getLinkage();

        }
        F.setLinkage(GlobalValue::CommonLinkage);
    }

    // For globals
    for(auto &G: M.globals()){

        if(saveBackup)
            backupLinkage4Globals[G.getName().str()] = G.getLinkage();

        G.setLinkage(GlobalValue::CommonLinkage);
    }
}

static std::set<size_t> moduleFunctionHashes;
static std::hash<std::string> hasher;

static bool is_same_func(std::string function_name, std::string module_file, bool saveIfNotIn=true, size_t worker=0){

    LLVMContext context;
    SMDiagnostic error;

    auto module = parseIRFile(module_file, error, context);

    auto fObject = module->getFunction(function_name);
    deinternalize_module(*module);

    std::string fObjectDump;
    llvm::raw_string_ostream fObjectDumpSS(fObjectDump);
    // TODO Avoid function name
    fObjectDumpSS << *fObject;

    if(DebugLevel > 2)
        errs() << "Hashing " << function_name << " " << module_file << " size " << fObjectDump.size() << " w:" << worker <<  "\n";

    size_t hash = hasher(fObjectDump);


    if(moduleFunctionHashes.count(hash)){ // Already exist
        errs() <<  function_name << " already exist in " << module_file  << " w:" << worker <<  "\n";;
        return true;
    }

    if(DebugLevel > 2) {
        errs() << "Saving variant for " << function_name << " " << module_file << " hash " << hash << " w:" << worker <<  "\n";;

        if(DebugLevel > 4){
            errs() << fObjectDump << "\n";
        }
    }


    moduleFunctionHashes.insert(hash);

    if(DebugLevel > 2)
        errs() << "Function " << function_name << " " << module_file << " inserted  w:" << worker <<  "\n";

    return false;
}

static void restore_linkage(Module &M){

    // For functions
    for(auto &F: M){
        if(backupLinkage4Functions.count(F.getName().str())) {
            if(DebugLevel > 3)
                errs() << "Restoring linkage for " << F.getName() << "\n";
            F.setLinkage(backupLinkage4Functions[F.getName().str()]);
        }
    }

    // For globals
    for(auto &G: M.globals()){

        if(backupLinkage4Globals.count(G.getName().str()))
            G.setLinkage(backupLinkage4Globals[G.getName().str()]);
    }
}

static bool is_a_variant(std::string &fname){

    for(auto &kv: origingalVariantsMap){
        for(auto v: kv.second){
            if(fname == v)
                return true;
        }
    }

    return false;
}

static void addVariant(std::string &original, std::string &variantName){

    if(DebugLevel > 2)
        errs()  << "Adding new entry for " << original << " variant: " << variantName <<  "\n";

    if(origingalVariantsMap.count(original) == 0){
        // Create the entry
        std::vector<std::string> v;
        origingalVariantsMap[original] = v;
    }

    origingalVariantsMap[original].push_back(variantName);
}


static cl::opt<unsigned> ParallelWorkers(
        "parallel-workers",
        cl::desc("Number of paralleling inferring to get valid replacements"),
        cl::init(1200)); // if the cunk_size is less than 1000, do the saving

template<typename Iterator>
typename std::iterator_traits<Iterator>::value_type
save_init_functions_in_parallel(unsigned level_in, Iterator in, Iterator end, unsigned size){
    if(level_in == ParallelWorkers){
        errs() << " " << std::addressof(in) << " " << std::addressof(end)  << "\n";

    }else{
        unsigned middle = size/2;
        save_init_functions_in_parallel(level_in + 1, in, std::next(in, middle), middle);
        save_init_functions_in_parallel(level_in + 1, std::next(in, middle), end, size - middle);
    }
}

template<typename Iterator,typename Func>
void parallel_for_each(Iterator first,Iterator last,Func f)
{
    ptrdiff_t const range_length=std::distance(first,last);
    //if(!range_length)
    //    return;
    if(range_length <= ParallelWorkers)
    {
        // errs() << "\nCalling f "<< std::addressof(first) << " " << range_length << "\n";
        unsigned it = 0;
        for(auto i = first; i != last; i++ ){
            f(*i, it++);
        }
        return;
    }

    //errs() << "\nSpliting "<< range_length << "\n";
    Iterator const mid=std::next(first,(range_length/2));

    std::future<void> bgtask = std::async(&parallel_for_each<Iterator,Func>,first,mid,f);
    parallel_for_each(mid,last,f);
    bgtask.get();
    // bgtask.wait();
}

void save_init_functions(Module& bitcode){
    if(ParallelWorkers > 1) {
        // TODO, set limits for asyncs
        errs() << "Hashing functions in parallel: " << bitcode.size() << "\n";
        parallel_for_each(
                bitcode.begin(),
                bitcode.end(),
                [](auto &&function, unsigned w) {
                    is_same_func(function.getName().str(), InputFilename, true, w );
                }
        );
    }else{
        for(auto &F: bitcode){
            is_same_func(F.getName().str(), InputFilename);
        }
    }
}

int main(int argc, const char **argv) {

    // General stats
    unsigned added = 0;

    cl::ParseCommandLineOptions(argc, argv);

    LLVMContext context;
    SMDiagnostic error;

    errs() << "Parsing original bitcode " << InputFilename <<"\n";

    auto bitcode = parseIRFile(InputFilename, error, context);

    errs() << "Creating linker " << error.getMessage() <<"\n";

    Linker linker(*bitcode);

    if(DebugLevel > 1) {
        errs() << "Modules count " << BCFiles.size() << "\n";
        errs() << "Function count " << FunctionNames.size() << "\n";
    }
    // Deinternalize functions
    if(!CompleteReplace)
        deinternalize_module(*bitcode, /*save linkage as backup*/ true);



    //
    if(DebugLevel > 1) {
        errs() << "Hashing original functions " << BCFiles.size() << "\n";
    }

    save_init_functions(*bitcode);

    errs() << "Injecting variants from " << BCFiles.size() << " modules\n";

    // Declare _cb71P5H47J3A(i: i32) -> void
    if(DebugLevel > 2)
        errs() << "Injecting instrumentation callback\n";

    Function * fCb = nullptr;
    if(InstrumentFunction || InstrumentBB){
        fCb =  declare_function_instrument_cb(*bitcode, context);
    }

    // Set override flag
    unsigned Flags = Linker::Flags::None;

    if(Override)
        Flags |=  Linker::Flags::OverrideFromSrc;


    if(DebugLevel > 2)
        errs() << "Merging modules\n";

    int c = 0;
    auto start_at = std::chrono::system_clock::now();

    for(auto &module: BCFiles) {
        auto delta = std::chrono::system_clock::now() - start_at;
        outs() << "\r" << module << " " << c++ << "/" << BCFiles.size() << " since " << delta.count()/1000000 << "s " ;

        if (DebugLevel > 3)
            errs() << "Merging module " << module << "\n";

        if (!exists(module)) {

            if (DebugLevel > 1)
                errs() << "Module " << module << " does not exist\n";

            continue; // continue since the module does not exist
        }

        try{ 
            auto toMergeModule = parseIRFile(module, error, context);


            if(!CompleteReplace)
                deinternalize_module(*toMergeModule);

            std::vector<std::string> toMergeFunctions;


            if (!NotLookForFunctions && !FunctionNames.empty()) {

                if (DebugLevel > 2)
                    errs() << "Using user defined function variants" << module << "\n";

                for(auto &fname: FunctionNames)
                    toMergeFunctions.push_back(fname);
            }
            else{
                if (DebugLevel > 2)
                    errs() << "Using all defined functions as variants inside module " << module << "\n";

                // Add all functions in new module as probable variant functions
                for(auto &func: *bitcode)
                    if(!func.isDeclaration()) {
                        auto fName = func.getName().str();
                        if(!is_a_variant(fName)) {

                            if(!fName.empty()) {
                                toMergeFunctions.push_back(fName);

                                if (DebugLevel > 2)
                                    errs() << "\t'" << func.getName() << "\n";
                            }
                        }
                    }
            }



            outs() << " f count " << toMergeFunctions.size() << "                    ";
            if (DebugLevel > 1)
                errs() << " Merging module " << module << "\n";
            for (auto &fname : toMergeFunctions) {

                if (DebugLevel > 2)
                    errs() << "Adding function " << fname << " from module " << module << "\n";

                if (fname.empty())
                    continue;

                if (DebugLevel > 2)
                    errs() << "Getting function object" << "\n";

                auto *fObject = toMergeModule->getFunction(fname);

                if (DebugLevel > 2)
                    errs() << "Checking if it is a function definition" << "\n";

                if (fObject == NULL || fObject->isDeclaration())
                    continue;

                if (DebugLevel > 2)
                    errs() << "\tMerging function " << fname << "\n";

                // replace by variant if signature is the same

                if(CompleteReplace){

                    if (DebugLevel > 2)
                        errs() << "\t Relying on override flag to override original function" << "\n";
                    // check that linker override flag is set

                    continue;
                }

                if (InjectOnlyIfDifferent) {

                    if (DebugLevel > 2)
                        errs() << "\t Cheking for identical function" << "\n";

                    if (is_same_func(fname, module)) {

                        if (DebugLevel > 2)
                            errs() << "\t Removing identical function " << fname << " in " << module << "\n";

                        continue;
                    }

                }

                std::string newName;
                llvm::raw_string_ostream newNameOutput(newName);
                newNameOutput << fname << "_" << modulesCount << FuncSufix;
                newNameOutput.flush();


                // Check if the function has a special linkage
                if (backupLinkage4Functions.count(fObject->getName().str())) // Set the nw function type as the original
                    backupLinkage4Functions[newName] = backupLinkage4Functions[fObject->getName().str()];

                // Change function name
                fObject->setName(newNameOutput.str());

                variantsMap4Instrumentation.insert_or_assign(fObject->getName().str(), 1);

                errs() << "Variants count " << variantsMap4Instrumentation.size() << "\n";
                if(NoInline){
                    fObject->addFnAttr(Attribute::NoInline);
                }

                if (DebugLevel > 2)
                    errs() << "Ready to merge " << newNameOutput.str() << "\n";

                if (DebugLevel > 2)
                    errs() << newNameOutput.str() << "\n";
                added++;

                auto original = bitcode->getFunction(fname);

                if (original) {
                    addVariant(fname, newNameOutput.str());
                } else {
                    errs() << "WARNING: " << "original bitcode does not contain the function " << fname << "\n";
                }
            }

            linker.linkInModule(std::move(toMergeModule), Flags);
        }
        catch(...) {
            errs() << "Error merging variant \n";
        }
        modulesCount++;
    }


    mewe_linker::merge_variants(*bitcode, context, origingalVariantsMap, variantsMap4Instrumentation);
    // Restore initial function and global linkage

    if(!CompleteReplace)
        restore_linkage(*bitcode);

    mewe_linker::instrument_functions(fCb, *bitcode, variantsMap4Instrumentation);

    if(NoInline){
        // Annotate all functions with no inline allowed
        for(auto &F: *bitcode){
            F.addFnAttr(Attribute::NoInline);
        }
    }

    std::error_code EC;
    llvm::raw_fd_ostream OS(OutFileName, EC);


    WriteBitcodeToFile(*bitcode, OS);
    OS.flush();

    errs() << "Added functions " << added << "\n";

    return 0;
}
