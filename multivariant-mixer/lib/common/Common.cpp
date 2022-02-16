//
// Created by Javier Cabrera on 2021-05-10.
//

#include "common/Common.h"

extern unsigned DebugLevel;

namespace crow_linker {
    bool exists (const std::string& name) {
        struct stat buffer;
        return (stat (name.c_str(), &buffer) == 0);
    }


}