//
// Created by Javier Cabrera on 2021-05-10.
//

#ifndef CROWMERGE_INSTRUMENTOR_H
#define CROWMERGE_INSTRUMENTOR_H


#include "llvm/Support/CommandLine.h"
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <common/Common.h>

using namespace llvm;

namespace crow_linker {
    Function* declare_function_instrument_cb(Module &M, LLVMContext &context);
    void instrument_functions(Function* fCb, Module &bitcode, std::map<std::string, char> &variantsMap);
}


#endif //CROWMERGE_INSTRUMENTOR_H