#ifndef ANALYSIS_EXTERN_C_H
#define ANALYSIS_EXTERN_C_H


#include <string>


#ifdef __cplusplus
extern "C" {
#endif


/**
 * @struct FileStatsBase
 * @brief Base structure for file statistics.
 * 
 * Represents the statistics to be computed.
 * Prevents copying to ensure safe management of the memory, which is handled by FileStats.
 */
struct FileStatsBase {
    char* path_cstr; // C-style dynamic string, to be moved, not copied.
    int empty_lines;
    int trivial_lines;
    int import_lines;
    int comment_lines;
    int multistring_lines;
    int logging_lines;
    int code_lines;
    int total_lines;
    int total_classes;

protected:
    FileStatsBase();

    FileStatsBase(const FileStatsBase&) = delete;
    FileStatsBase& operator=(const FileStatsBase&) = delete;

    FileStatsBase(FileStatsBase&& other) = default;
    FileStatsBase& operator=(FileStatsBase&& other) = default;

    friend class FileStats;
};

/**
 * @struct FileStats
 * @brief Manages C-string memory for `FileStatsBase`.
 * 
 * Implements move semantics and disallows copying to ensure safe handling of the C-string.
 */
struct FileStats : public FileStatsBase {
public:
    FileStats();
    FileStats(const std::string& path);

    FileStats(FileStats&& other) noexcept;
    FileStats& operator=(FileStats&& other) noexcept;

    ~FileStats();

    FileStats(const FileStats&) = delete;
    FileStats& operator=(const FileStats&) = delete;
};


/**
 * @brief Analyzes multiple files and returns their statistics.
 *
 * @param paths An array of file paths.
 * @param contents An array of file contents corresponding to the paths.
 * @param count The number of files to analyze.
 * @return A pointer to an array of FileStats structures, or nullptr on error.
 *         The caller is responsible for freeing this memory using delete[].
 * @throws std::invalid_argument if any path or content pointer is null.
 */
FileStats* analyzeFiles(const char** paths, const char** contents, int count);

/**
 * @brief Frees the memory allocated for a FileStats array.
 *
 * @param stats Pointer to the FileStats array to be freed.
 * @param count Number of elements in the FileStats array.
 */
void freeFileStats(FileStats* stats, int count);


#ifdef __cplusplus
} // extern "C"
#endif


#endif // ANALYSIS_EXTERN_C_H
