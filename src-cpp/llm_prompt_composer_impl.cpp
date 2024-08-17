#include "llm_prompt_composer_impl.h"

#include <sstream>
#include <vector>
#include <string>


std::vector<std::string> LlmPromptComposer::composePromptLines(
    const std::vector<std::pair<std::string, std::string>>& path_and_contents) const {
    std::vector<std::string> lines;

    composePreamble(&lines);
    composeFilesAndContents(path_and_contents, &lines);
    composeInstructions(&lines);

    return lines;
}

void LlmPromptComposer::composePreamble(std::vector<std::string>* out_lines) const {
    out_lines->insert(out_lines->end(), {
        "Assist me in improving programming code.",
        "Find below file paths and contents marked with '==='.",
        "Analyze and provide suggestions for improvement.",
        "",
    });
}

void LlmPromptComposer::composeFilesAndContents(
    const std::vector<std::pair<std::string, std::string>>& path_and_contents,
    std::vector<std::string>* out_lines) const {
    for (const auto& [path, content] : path_and_contents) {
        out_lines->insert(out_lines->end(), {
            "=== FILE PATH ===",
            path,
            "",
            "=== FILE CONTENT ===",
            content,
            "",
        });
    }
}

void LlmPromptComposer::composeInstructions(std::vector<std::string>* out_lines) const {
    out_lines->insert(out_lines->end(), {
        "Start with the most critical / important improvements pick 1 to 3 items.",
        "Look for code issues, design issues, code formatting, simplifications.",
        "Apply best practices, make recommendations for using most common and widely recognized",
        "approaches.",
        "Assume code line length should not exceed 100 chars, break if needed with",
        "holding good indentations. Also in case too fast line break does not make sense,",
        "join lines.",
        "Provide the following:",
        "1. Explain issue / improvement you identify in the code.",
        "2. Suggest the change.",
        "",
        "After your explanation and suggestions, please provide an explicit diff patch snippet",
        "that applies your suggested improvements. Separate this patch with the marker:",
        "'=== DIFF PATCH SNIPPET BELOW ===' and '=== DIFF PATCH SNIPPET ABOVE ==='",
        "Please ensure the diff patch is in a standard format i.e. similar to",
        "diff -ruN and can be applied via patch << your_snippet.txt.",
    });
}
