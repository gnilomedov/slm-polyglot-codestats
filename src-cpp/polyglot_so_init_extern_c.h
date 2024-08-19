#ifndef POLYGLOT_LOGGING_H
#define POLYGLOT_LOGGING_H


/**
 * @brief External C linkage block
 *
 * Prevents C++ name mangling, enabling C and FFI compatibility.
 * Allows calling from other languages (e.g., Python via ctypes).
 */
#ifdef __cplusplus
extern "C" {
#endif


void initPolyglot(const char* programName);


#ifdef __cplusplus
}
#endif


#endif // POLYGLOT_LOGGING_H
