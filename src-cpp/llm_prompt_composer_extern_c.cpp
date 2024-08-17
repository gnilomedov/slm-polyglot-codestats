#include "llm_prompt_composer_extern_c.h"

#include <cstring>
#include <sstream>
#include <stdexcept>
#include <string>

#include "llm_prompt_composer_impl.h"


extern "C" {

char* composeCodeImprovePrompt(const char** paths, const char** contents, int count) {
    if (count < 0) {
        throw std::invalid_argument("Invalid input count");
    }
    std::vector<std::pair<std::string, std::string>> path_and_contents;
    for (int i = 0; i < count; ++i) {
        if (!paths[i] || !contents[i]) {
            throw std::invalid_argument("Null path or content pointer");
        }
        path_and_contents.emplace_back(paths[i], contents[i]);
    }

    LlmPromptComposer composer;
    auto lines = composer.composePromptLines(path_and_contents);
    std::ostringstream oss;
    for (const auto& line : lines) {
        oss << line << "\n";
    }

    std::string str = oss.str();
    char* result = new char[str.length() + 1];
    std::strcpy(result, str.c_str());

    return result;
}

void freeComposedPrompt(char* prompt) {
    delete[] prompt;
}

} // extern "C"
