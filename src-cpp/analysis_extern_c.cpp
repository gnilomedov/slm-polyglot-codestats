#include "analysis_extern_c.h"

#include <memory>
#include <new>
#include <stdexcept>
#include <type_traits>
#include <utility>
#include <vector>

#include "src_analysis_calculator.h"


/**
 * @brief External C linkage block
 *
 * Prevents C++ name mangling, enabling C and FFI compatibility.
 * Allows calling from other languages (e.g., Python via ctypes).
 */
extern "C" {


FileStats* analyzeFiles(const char** paths, const char** contents, int count) {
    if (count <= 0 || paths == nullptr || contents == nullptr) {
        return nullptr;
    }

    std::vector<FileStats> file_stats_vec;
    file_stats_vec.reserve(count);
    for (int i = 0; i < count; ++i) {
        if (paths[i] == nullptr || contents[i] == nullptr) {
            throw std::invalid_argument("Null path or content pointer");
        }
        SrcAnalysisCalculator calculator(paths[i]);
        file_stats_vec.emplace_back(calculator.analyze(contents[i]));
    }

    FileStats* output = new FileStats[file_stats_vec.size()];
    std::move(file_stats_vec.begin(), file_stats_vec.end(), output);
    return output;
}

void freeFileStats(FileStats* stats, int count) {
    delete[] stats;
}


FileStatsBase::FileStatsBase()
    : path_cstr(nullptr),
      empty_lines(0),
      trivial_lines(0),
      import_lines(0),
      comment_lines(0),
      multistring_lines(0),
      logging_lines(0),
      code_lines(0),
      total_lines(0),
      total_classes(0) {
}

FileStats::FileStats(): FileStatsBase() {}

FileStats::FileStats(const std::string& path): FileStatsBase() {
    path_cstr = new char[path.size() + 1];
    std::strcpy(path_cstr, path.c_str()); // std::strcpy guarantees null-termination.
}

FileStats::FileStats(FileStats&& other) noexcept : FileStatsBase(std::move(other)) {
    other.path_cstr = nullptr;
}

FileStats& FileStats::operator=(FileStats&& other) noexcept {
    if (this != &other) {
        delete[] path_cstr;
        FileStatsBase::operator=(std::move(other));
        path_cstr = other.path_cstr;
        other.path_cstr = nullptr;
    }
    return *this;
}

FileStats::~FileStats() {
    delete[] path_cstr;
    path_cstr = nullptr;
}


// Ensure that FileStats does not add fields.
static_assert(sizeof(FileStats) == sizeof(FileStatsBase), 
              "FileStats only adds move constructor, not fields to FileStatsBase.");


}  // extern "C"
