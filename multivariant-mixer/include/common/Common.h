//
// Created by Javier Cabrera on 2021-05-10.
//

#ifndef CROWMERGE_COMMON_H
#define CROWMERGE_COMMON_H


#include <map>
#include <llvm/IR/GlobalValue.h>
#include <sys/stat.h>
#include "llvm/Support/CommandLine.h"

#ifdef __APPLE__
#include <dispatch/dispatch.h>
#else
#include <semaphore.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/wait.h>
#endif

using namespace llvm;

namespace crow_linker{

    static std::map<std::string, GlobalValue::LinkageTypes> backupLinkage4Functions;


    #ifndef Map4Instrumentation
    #define Map4Instrumentation
    static std::map<std::string, char> variantsMap4Instrumentation;
    #endif

    static std::map<std::string, GlobalValue::LinkageTypes> backupLinkage4Globals;
    static std::map<std::string, std::vector<std::string>> origingalVariantsMap;

    // Check if file exists
    bool exists (const std::string& name);
}


#endif