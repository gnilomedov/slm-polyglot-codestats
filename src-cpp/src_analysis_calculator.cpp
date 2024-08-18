#include "src_analysis_calculator.h"

#include <iostream>
#include <cassert>
#include <sstream>

#include <glog/logging.h>


SrcAnalysisCalculator::SrcAnalysisCalculator(const std::string& path)
    : TRIM_REGEX("^\\s+|\\s+$"),
      TRIVIAL_REGEX("^[}\\])]$"),
      IMPORT_REGEX("^(\\s*(import|#include|using)\\s+.*|from\\s+\\w+\\s+import\\s+.*)$"),
      COMMENT_REGEX("^(//|#).*$"),
      MULTISTRING_REGEX(".*(\"\"\"|\'\'\').*$"),
      LOGGING_REGEX(R"(.*(\[\s*(debug|info|warn|error)\s*\]|log(ger)?\.(debug|info|warn|error)|)"
	                R"(log\s*\(\s*(debug|info|warn|error)\s*\)).*)",
	                std::regex::icase),
      CLASS_REGEX("(public|protected|private|data\\s+)?(class|interface|enum|struct)\\s+\\w+.*$"),
      FORWARD_DECLARATION_REGEX("class\\s+\\w+\\s*;$"),
      in_multiline_comment(false),
      in_multiline_string(false),
      stats(path) {
}

namespace {

std::string getFileName(const std::string& fullPath) {
    size_t pos = fullPath.find_last_of("/\\");
    return (pos == std::string::npos) ? fullPath : fullPath.substr(pos + 1);
}

} // namespace

FileStats SrcAnalysisCalculator::analyze(const std::string& content) {
    std::istringstream iss(content);
    std::string line;
    while (std::getline(iss, line)) {
        ++stats.total_lines;
        classifyLine(line);
    }
    LOG(INFO) << getFileName(stats.path_cstr) << " : " << stats.total_lines;

    // FileStats is movable but non-copyable by design.
    // std::move explicitly indicates the transfer of ownership.
    // Return Value Optimization (RVO) might apply.
    return std::move(stats);
}

void SrcAnalysisCalculator::classifyLine(const std::string& line) {
    std::string trimmed_line = std::regex_replace(line, TRIM_REGEX, "");

    if (trimmed_line.find("/*") != std::string::npos) {
        in_multiline_comment = true;
    }

    if (trimmed_line.empty()) {
        ++stats.empty_lines;
    } else if (std::regex_match(trimmed_line, TRIVIAL_REGEX)) {
        ++stats.trivial_lines;
    } else if (std::regex_match(trimmed_line, IMPORT_REGEX)) {
        ++stats.import_lines;
    } else if (std::regex_match(trimmed_line, COMMENT_REGEX) || in_multiline_comment) {
        ++stats.comment_lines;
    } else if (std::regex_match(trimmed_line, MULTISTRING_REGEX) || in_multiline_string) {
        ++stats.multistring_lines;
    } else if (std::regex_match(trimmed_line, LOGGING_REGEX)) {
        ++stats.logging_lines;
    } else if (std::regex_match(trimmed_line, CLASS_REGEX)) {
        if (!std::regex_match(trimmed_line, FORWARD_DECLARATION_REGEX)) {
            ++stats.total_classes;
        }
    } else {
        ++stats.code_lines;
    }

    if (trimmed_line.find("*/") != std::string::npos) {
        in_multiline_comment = false;
    }

    if (!std::regex_match(trimmed_line, COMMENT_REGEX) &&
            (trimmed_line.find("\"\"\"") != std::string::npos ||
                trimmed_line.find("'''") != std::string::npos)) {
        in_multiline_string = !in_multiline_string;
        if (in_multiline_string) {
            ++stats.multistring_lines;
        }
    }
}
