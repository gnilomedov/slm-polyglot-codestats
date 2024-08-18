#ifndef LLM_PROMPT_COMPOSER_EXTERN_C_H
#define LLM_PROMPT_COMPOSER_EXTERN_C_H


/**
 * @brief External C linkage block
 *
 * Prevents C++ name mangling, enabling C and FFI compatibility.
 * Allows calling from other languages (e.g., Python via ctypes).
 */
#ifdef __cplusplus
extern "C" {
#endif


/**
 * @brief Composes a prompt for code improvement based on multiple files.
 *
 * @param paths An array of file paths.
 * @param contents An array of file contents corresponding to the paths.
 * @param count The number of files to analyze.
 * @return A pointer to a null-terminated C-string containing the composed prompt.
 *         The caller is responsible for freeing this memory using freeComposedPrompt().
 * @throws std::invalid_argument if any path or content pointer is null.
 */
char* composeCodeImprovePrompt(const char** paths, const char** contents, int count);

/**
 * @brief Frees the memory allocated by composeCodeImprovePrompt.
 *
 * @param prompt Pointer to the C-string returned by composeCodeImprovePrompt.
 */
void freeComposedPrompt(char* prompt);


#ifdef __cplusplus
} // extern "C"
#endif


#endif // LLM_PROMPT_COMPOSER_EXTERN_C_H
