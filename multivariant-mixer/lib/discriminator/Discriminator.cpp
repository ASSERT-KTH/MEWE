//
// Created by Javier Cabrera on 2021-05-10.
//
#include "discriminator/Discriminator.h"

using namespace llvm;
using namespace crow_linker;
extern unsigned DebugLevel;

std::string MergeFunctionSuffix;
bool MergeFunctionAsPtr;
bool MergeFunctionAsSCases;
bool NoInline;
bool AggressiveNoInline;
std::string DiscrminatorCallbackName;

namespace crow_linker {

    static cl::opt<std::string, /*ExternalStorage=*/ true> MergeFunctionSuffixFlag("merge-function-suffix",
                                                    cl::desc("N1 diversifier function suffix"),
            cl::location(MergeFunctionSuffix)
            , cl::init("_n1"));

    static cl::opt<bool, /*ExternalStorage=*/ true> MergeFunctionAsPtrFlag("merge-function-ptrs",
                                            cl::desc("Create the discrminator based on a global array of ptrs, accessing the function by the index in the array. This will create a Wasm table alter if the target is wasm32")
            , cl::location(MergeFunctionAsPtr)
                                            , cl::init(false));

    static cl::opt<bool, /*ExternalStorage=*/ true> MergeFunctionAsSCasesFlag("merge-function-switch-cases",
                                               cl::desc("Create the discrminator based on a huge switch case."),
            cl::location(MergeFunctionAsSCases)
            , cl::init(false));


    static cl::opt<std::string, /*ExternalStorage=*/ true> DiscrminatorCallbackNameFlag("discrminator-callback-function-name",
                                                         cl::desc("Callback function name to get the discriminator"),
           cl::location(DiscrminatorCallbackName) , cl::init("discriminate"));



    static cl::opt<bool> FullDiversifier("replace-all-calls-by-the-discriminator",
                                                                           cl::desc("Replace all calls to discriminator ")

            , cl::init(false));


    static cl::opt<bool, /*ExternalStorage=*/ true> NoInlineFlag("variants-no-inline",
                                                                           cl::desc("Annotate variant functions to avoid inlining")
            , cl::location(NoInline)
            , cl::init(false));

    static cl::opt<bool, /*ExternalStorage=*/ true> AggressiveNoInlineFlag("aggressive-no-inline",
                                                                 cl::desc("Annotate all functions to avoid inlining")
            , cl::location(AggressiveNoInline)
            , cl::init(false));



    static void printVariantsMap(){
        for(auto &key: origingalVariantsMap){
            errs() << key.first << ": " << key.second.size() + 1 << " " << &key << "\n";

            if (DebugLevel > 5){
                for(auto &v: origingalVariantsMap[key.first]){
                    errs() << &v;
                    //if(v->getName().str())
                    errs() << " " << v;
                    errs() << "\n";
                }
            }
        }
    }

    void create_switch_case_variant(Function *callee,Module &M, LLVMContext &context, Function& original, Function& discrminate, std::vector<std::string> &variants){



        unsigned IDX = 0;
        auto originalArgs = original.args().begin();
        for(auto &arg: callee->args()){
            arg.setName(originalArgs[IDX++].getName());
        }


        IRBuilder<> Builder(context);

        BasicBlock *BB = BasicBlock::Create(context, "entry", callee);
        Builder.SetInsertPoint(BB);

        std::vector<Value*> discriminatorArgs ;
        discriminatorArgs.push_back(
                ConstantInt::get(Type::getInt32Ty(context), variants.size() + 1) // pass the number of variants plus the original
        );
        auto discriminateValue = Builder.CreateCall(&discrminate, discriminatorArgs, "");

        if (DebugLevel > 4)
            errs() << "Building the switch case " << variants.size() << "\n";

        std::vector<Value*> Values;
        for (auto &Arg : callee->args()) {
            Values.push_back(&Arg);
        }
        auto name = original.getName().str();

        variantsMap4Instrumentation.insert_or_assign(name, 1); // add dispatcher

        errs() << "Finishing the switch case for " << name << ". Final size " << variants.size() + 1 << "\n";
        errs() << "size " << variantsMap4Instrumentation.size() << "\n";

        std::vector<BasicBlock*> bbs;
        for(auto &variant: variants) {


            std::string bbName;
            llvm::raw_string_ostream bbNameOutput(bbName);
            bbNameOutput << "case_" << variant;

            if (DebugLevel > 4)
                errs() << "Variant case " << bbName << "\n";

            BasicBlock *caseBB = BasicBlock::Create(context,bbName, callee);

            bbs.push_back(caseBB);
        }

        if (DebugLevel > 4)
            errs() << "BB created" << "\n";

        BasicBlock *EndBB = BasicBlock::Create(context, "end", callee);
        auto phi = Builder.CreateSwitch(discriminateValue, EndBB, variants.size());

        IDX=0;
        for(auto &variant: variants) {

            auto func = M.getFunction(variant);

            auto *bid = llvm::ConstantInt::get(Type::getInt32Ty(context), IDX);
            phi->addCase(bid, bbs[IDX++]);

            if(func->getReturnType() != Type::getVoidTy(context)) {
                Builder.CreateRet(
                        Builder.CreateCall(func, Values, "")
                );
            }
            else
            {

                Builder.CreateCall(func, Values, "");
                Builder.CreateRetVoid();
            }

        }

        if (DebugLevel > 4)
            errs() << "BB bodies created" << "\n";
        //Builder.SetInsertPoint(EndBB);

        if(original.getReturnType() != Type::getVoidTy(context))
            Builder.CreateRet(
                    Builder.CreateCall(&original, Values, "")
            );
        else {
            Builder.CreateCall(&original, Values, "");
            Builder.CreateRetVoid();
        }
        if (DebugLevel > 4)
            errs() << "Returning the switch case" << "\n";
    }


    void create_ptrs_variant(Function *callee,Module &M, LLVMContext &context, Function& original, Function& discrminate, std::vector<std::string> &variants){


        unsigned IDX = 0;
        auto originalArgs = original.args().begin();
        for(auto &arg: callee->args()){
            arg.setName(originalArgs[IDX++].getName());
        }

        IRBuilder<> Builder(context);

        // Create global table object
        std::string newName;
        llvm::raw_string_ostream newNameOutput(newName);
        newNameOutput << original.getName() << "_global_table";

        if(DebugLevel > 4)
            errs() << "Creating global object " << "\n";

        auto gType = ArrayType::get(
                original.getType(), variants.size() + 1);
        M.getOrInsertGlobal(newName, gType); // The variants + the original


        auto globalTable = M.getGlobalVariable(newName);
        globalTable->setLinkage(llvm::GlobalValue::InternalLinkage);
        globalTable->setConstant(true);

        // Set function pointers
        std::vector<llvm::Constant*> values;

        values.push_back(&original);

        for(auto &variant: variants){

            values.push_back(
                    M.getFunction(variant)
            );
        }

        auto init = llvm::ConstantArray::get(
                gType, values);
        globalTable->setInitializer(init);

        BasicBlock *BB = BasicBlock::Create(context, "entry", callee);
        Builder.SetInsertPoint(BB);


        if(DebugLevel > 4)
            errs() << "Calling discriminator " << "\n";

        std::vector<Value*> discriminatorArgs ;
        auto discriminateValue = Builder.CreateCall(&discrminate, discriminatorArgs, "");

        if(DebugLevel > 4)
            errs() << "Loading f pointer" << "\n";

        //auto tablePtr = Builder.CreateLoad(globalTable);

        if(DebugLevel > 4)
            errs() << "Loading f index" << "\n";

        auto elementPtr = Builder.CreateGEP(
                original.getType(),
                globalTable, discriminateValue);
        auto element = Builder.CreateLoad(elementPtr);

        std::vector<Value*> Values;
        for (auto &Arg : callee->args()) {
            Values.push_back(&Arg);
        }

        //elementPtr->dump();
        //element->dump();


        //auto cast = llvm::dyn_cast<Function*>(element);
        //auto elementMethod = dyn_cast<Function>(element);
        //cast->dump();

        auto fCall = Builder.CreateCall(original.getFunctionType(),element, Values,  ""
        );
        //errs() << element << "\n";

        //fCall->dump();

        Builder.CreateRet(fCall);

    }


    Function* declare_function_discriminator(Module &M, LLVMContext &context, std::string originalName, Function& discrminate, std::vector<std::string> &variants, std::map<std::string, char> &variantsMap){

        auto original = M.getFunction(originalName);

        std::string newName;
        llvm::raw_string_ostream newNameOutput(newName);
        if(!original->getName().empty())
            newNameOutput << original->getName() << "_" << MergeFunctionSuffix;
        else
            newNameOutput << "_" << MergeFunctionSuffix;

        auto linkage = backupLinkage4Functions[originalName];

        std::vector<Type*> args(0);
        FunctionType *tpe = original->getFunctionType();
        Function *callee = Function::Create(tpe, linkage, newName, M);

        variantsMap[newName] = 1;// original function is also a variant

        if(MergeFunctionAsSCases)
            create_switch_case_variant(callee, M, context, *original, discrminate, variants);
        if(MergeFunctionAsPtr){
            errs() << "Replace calls by indirect calls, TODO \n";
            exit(1);
        }
        // TODO create_ptrs_variant(callee, M, context, original, discrminate, variants);

        return callee;
    }

    Function* declare_function_discriminatee(Module &M, LLVMContext &context){

        std::vector<Type*> args(1,
                                Type::getInt32Ty(context));// the first argument is the number of variants
        FunctionType *tpe = FunctionType::get(Type::getInt32Ty(context), args,false);
        Function *callee = Function::Create(tpe, Function::ExternalLinkage, DiscrminatorCallbackName, M);

        if(DebugLevel > 2){
            // print all map etry count
            errs() << "Defined discrminate function " << "\n";
        }


        return callee;
    }

    bool can_replace(Function *f, std::vector<std::string> &fMap, std::string &originalName){
        auto name = f->getName();

        if(name.compare(originalName) == 0)
            return true;

        for(auto &kv: fMap){
            if(name.compare(kv) == 0)
                return true;
        }

        return false;
    }

    void full_diversification_replace(Module &bitcode, LLVMContext& context, Function* discrminatorF, std::vector<std::string> &fMap, std::string &originalName){


        for(auto &F: bitcode){
            // Avoid replacements inside discriminator
            if(&F == discrminatorF)
                continue;

            for(auto &BB: F){

                for(auto inst = BB.begin(); inst != BB.end(); ++inst){
                    if(isa<CallInst>(inst)){

                        auto c = cast<CallInst>(inst);

                        auto oldCalled = c->getCalledFunction();

                        if(oldCalled == NULL)
                            continue;

                        if(DebugLevel > 3){
                            errs() << "Replacing function call " << oldCalled->getName() << "\n";
                        }

                        if( can_replace(oldCalled, fMap, originalName)){

                            if(DebugLevel > 3){
                                //c->dump();
                                errs() << "Replaced function call " << oldCalled->getName() << "\n";
                            }

                            c->setCalledFunction(discrminatorF);
                        }
                    }
                }

            }
        }
    }

    void merge_variants(Module &bitcode, LLVMContext& context, std::map<std::string, std::vector<std::string>> &fMap, std::map<std::string, char> &variantsMap){

        if(MergeFunctionAsPtr || MergeFunctionAsSCases){

            if(DebugLevel > 4){
                // print all map etry count
                printVariantsMap();
            }
            // Register discrminator function as external
            if(DebugLevel > 2){
                // print all map etry count
                errs() << "Defining discrminate function " << "\n";
            }
            auto discriminate = declare_function_discriminatee(bitcode, context);
            if(DebugLevel > 2){
                // print all map etry count
                errs() << "Unique variants count " << fMap.size() << "\n";
            }
            // for each function in the map
            for(auto &kv: fMap){

                if(kv.second.empty()){
                    if(DebugLevel > 2)
                        errs() << "Skipping multivariant generation for " << kv.first << "\n";
                    continue;
                }

                if(DebugLevel > 2)
                    errs() << "Creating discrimination harness\n";

                if(DebugLevel > 2)
                    errs() << "Merging " << kv.first << " " << kv.second.size() <<  "\n";

                auto mergeFunction = declare_function_discriminator(bitcode, context, kv.first, *discriminate, kv.second, variantsMap);

                // rename original function
                Function *originalFunction = bitcode.getFunction(kv.first);

                std::string originalName;
                llvm::raw_string_ostream originalNameOutput(originalName);
                originalNameOutput << kv.first << "_original";
                originalFunction->setName(originalName);

                variantsMap.insert_or_assign(originalName, 1); // The original code is also a variant

                if(NoInline)
                    originalFunction->addFnAttr( Attribute::NoInline);

                // rename then discriminator function as the original
                mergeFunction->setName(kv.first);

                variantsMap.insert_or_assign(kv.first, 1); // The dispatcher as well

                // Avoid inlining
                if(NoInline)
                    mergeFunction->addFnAttr(Attribute::NoInline);

                if(FullDiversifier){

                    if(DebugLevel > 3){
                        errs() << "Replacing all calls \n";
                    }
                    // Iterate module and replace calls by X
                    full_diversification_replace(bitcode, context, mergeFunction, kv.second, originalName);
                }

                if(DebugLevel > 2)
                    errs()  << mergeFunction->getName() << "\n";
            }


        }
    }

}

