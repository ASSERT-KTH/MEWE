//
// Created by Javier Cabrera on 2021-05-10.
//
#include "instrumentor/Instrumentor.h"

using namespace llvm;
using namespace crow_linker;

extern unsigned DebugLevel;

bool InstrumentFunction;
bool InstrumentBB;
bool InstrumentOnlyVariants;

namespace crow_linker {

    static cl::opt<unsigned> StartIdAt(
            "crow-merge-id-start",
            cl::desc("Start the function mapping with this number. This will be valid only with the instrumentation flags"),
            cl::init(0));


    static cl::opt<bool, true>
            InstrumentFunctionFlag("instrument-function",
                                   cl::desc("Instrument first function basic block to construct the call graph. When linking ensure that a function _cb(i: i32) exist"),
                                   cl::location(InstrumentFunction),
                                   cl::init(false));

    static cl::list<std::string> ToInstrument("instrument-include",
                                         cl::desc("Functions to include for instrumentation")
            , cl::ZeroOrMore, cl::CommaSeparated);

    static cl::opt<bool, true>
            InstrumentBBFlag("instrument-bb",
                             cl::desc("Instrument basic blocks to construct the call graph. When linking ensure that a function _cb(i: i32) exist"),
                             cl::location(InstrumentBB),
                             cl::init(false));


    static cl::opt<bool, true>
            InstrumentOnlyVariantsFlag("instrument-only-variants",
                             cl::desc("Instrument only variants to detect calling"),
                             cl::location(InstrumentOnlyVariants),
                             cl::init(false));

    static cl::opt<std::string> InstrumentCallbackName("callback-function-name",
                                                       cl::desc("Callback function name for callgraph instrumentation")
            , cl::init("_cb71P5H47J3A"));



    Function* declare_function_instrument_cb(Module &M, LLVMContext &context){


        std::vector<Type*> args(1,
                                Type::getInt32Ty(context));
        FunctionType *tpe = FunctionType::get(Type::getVoidTy(context), args,false);
        Function *callee = Function::Create(tpe, Function::ExternalLinkage, InstrumentCallbackName, M);

        return callee;
    }


    static int instrumentId = 0;

    int instrument_BB(BasicBlock *BB, Function *fCb){

        if(DebugLevel > 2) {
            errs() << "Instrumenting ";
            //BB->dump();
        }
        // Construct call
        IRBuilder<> builder(BB);
        if (DebugLevel > 2)
            errs() << "Constructing call for " << BB->getParent()->getName() << " isDeclaration: " << BB->getParent()->isDeclaration()  << "\n";


        BasicBlock::iterator insertIn = BB->getFirstInsertionPt();
        while (isa<AllocaInst>(insertIn))  ++insertIn;

        Value *bid = llvm::ConstantInt::get(Type::getInt32Ty(BB->getContext()), instrumentId++);
        CallInst::Create(fCb, bid, "", cast<Instruction>(insertIn));

        if (DebugLevel > 2)
            errs() << "Inserting before" << *insertIn << "\n";

        return instrumentId - 1;
    }

    void instrument_functions(Function* fCb, Module &bitcode, std::map<std::string, char> &variantsMap){
        // Instrument for callgraph if needed
        if((InstrumentFunction || InstrumentBB) && fCb){
            instrumentId = StartIdAt;
            if(DebugLevel > 0)
                errs() << "Variants map size " << variantsMap.size() << "\n" ;
            // Add the optional instrumentation options to the map

            for(auto &name: ToInstrument)
                variantsMap.insert_or_assign(name, 1);

            if(DebugLevel > 2)
                errs() << "Instrumenting functions for callgraph"  << "\n";

            for(auto &F: bitcode){
                if(!F.isDeclaration()) {

                    if (DebugLevel > 2)
                        errs() << F.getName() << "Instrumenting basic blocks" << "\n";

                    // FILTER, if instrument only dispatchers and variants
                    if(InstrumentOnlyVariants){
                        auto name = F.getName().str();

                        if(variantsMap.count(name) == 0){ // the function should not be instrumented

                            if (DebugLevel > 2)
                                errs() << name << " is not a  variant" << "\n";
                            continue;
                        }
                    }
                    for(auto &BBA: F){
                        // Instrument all BB
                        int id = instrument_BB(&BBA, fCb);

                        // TODO, print map for future analysis
                        errs() << F.getName() << ", " << id << "\n";

                        if(!InstrumentBB && InstrumentFunction){
                            break;
                        }
                    }

                }
            }

        }
    }
}