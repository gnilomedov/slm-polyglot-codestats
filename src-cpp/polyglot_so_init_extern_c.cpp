#include "polyglot_so_init_extern_c.h"

#include <iostream>

#include <glog/logging.h>


extern "C" {


void initPolyglot(const char* programName) {
    std::cout << "initPolyglot '" << programName << "' ..." << std::endl;
    /**
     * If enabled, log messages disappear, otherwise just get:
     * WARNING: Logging before InitGoogleLogging() is written to STDERR
     * TODO: discover why.
    google::InitGoogleLogging(programName);
     */
    LOG(INFO) << "Init '" << programName << "' - Done.";
}


}
