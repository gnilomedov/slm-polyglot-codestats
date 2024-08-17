#ifndef LLM_PROMPT_COMPOSER_IMPL_H
#define LLM_PROMPT_COMPOSER_IMPL_H

#include <vector>
#include <string>


/** A class for composing prompts for code improvement requests. */
class LlmPromptComposer {
public:
    LlmPromptComposer() = default;

    /**
     * @brief Composes a complete prompt from file paths and contents.
     *
     * Combines a list of file paths and their corresponding contents with predefined sections to
     * create a formatted prompt.
     *
     * @param path_and_contents A vector of pairs, each containing a file path and its contents.
     * @return A vector of strings representing the composed prompt lines.
     */
    std::vector<std::string> composePromptLines(
    const std::vector<std::pair<std::string, std::string>>& path_and_contents) const;

private:
    /** Appends the prompt preamble. */
    void composePreamble(std::vector<std::string>* out_lines) const;

    /** Appends file paths and contents. */
    void composeFilesAndContents(
        const std::vector<std::pair<std::string, std::string>>& path_and_contents,
        std::vector<std::string>* out_lines) const;

    /** Appends the prompt instructions. */
    void composeInstructions(std::vector<std::string>* out_lines) const;
};

#endif // LLM_PROMPT_COMPOSER_IMPL_H
