#ifndef SRC_ANALYSIS_CALCULATOR_H
#define SRC_ANALYSIS_CALCULATOR_H


#include <regex>
#include <string>

#include "analysis_extern_c.h"


/**
 * @brief Analyzes source code files and classifies lines.
 *
 * This class encapsulates the logic for analyzing a source code file and
 * classifying each line. It maintains internal state to track multiline
 * comments and strings across multiple lines. Note that it should not be
 * reused for analyzing multiple contents; create a new instance for each
 * analysis.
 *
 * Usage:
 * SrcAnalysisCalculator calculator(file_path);
 * FileStats stats = calculator.analyze(file_content);
 */
class SrcAnalysisCalculator {
private:
    const std::regex TRIM_REGEX;
    const std::regex TRIVIAL_REGEX;
    const std::regex IMPORT_REGEX;
    const std::regex COMMENT_REGEX;
    const std::regex MULTISTRING_REGEX;
    const std::regex LOGGING_REGEX;
    const std::regex CLASS_REGEX;
    const std::regex FORWARD_DECLARATION_REGEX;

    bool in_multiline_comment;
    bool in_multiline_string;

    FileStats stats;

public:
    /**
     * @brief Constructs a SrcAnalysisCalculator object.
     * @param path The path of the file to be analyzed.
     */
    SrcAnalysisCalculator(const std::string& path);

    /**
     * @brief Analyzes the given file content.
     * @param content The content of the file to analyze.
     * @return FileStats object containing the analysis results.
     */
    FileStats analyze(const std::string& content);

private:
    void classifyLine(const std::string& line);
};


#endif // SRC_ANALYSIS_CALCULATOR_H
