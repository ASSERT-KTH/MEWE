//
// Created by Javier Cabrera on 2021-05-10.
//

#ifndef CROWMERGE_DISCRIMINATOR_H
#define CROWMERGE_DISCRIMINATOR_H


#include "llvm/Support/CommandLine.h"
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <common/Common.h>

namespace crow_linker {
    void merge_variants(Module &bitcode, LLVMContext& context, std::map<std::string, std::vector<std::string>> &fMap, std::map<std::string, char> &variantsMap);
}


#endif //CROWMERGE_DISCRIMINATOR_H