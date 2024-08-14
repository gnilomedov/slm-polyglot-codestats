package demo.polyglot

import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.File
import java.io.IOException

/**
 * Represents the content of a file along with its path.
 *
 * @property path The absolute path of the file.
 * @property content The text content of the file.
 */
data class FileContent(val path: String, val content: String)

/**
 * Scans the specified folders for files with given extensions and returns their contents.
 *
 * @param folders A list of folder paths to scan.
 * @param extensions A list of file extensions to filter by (with or without leading dot).
 * @return A list of FileContent objects representing the matching files and their contents.
 * @throws IOException if there's an error reading a file.
 */
@Throws(IOException::class)
fun scanFolders(folders: List<String>, extensions: List<String>): List<FileContent> {
    val logger: Logger = LoggerFactory.getLogger("FileScanner")
    val normalizedExtensions = extensions.map { it.removePrefix(".") }
    var totalSize = 0L
    var totalCount = 0

    val fileContents = folders.flatMap { folder ->
        File(folder).walk()
            .filter { file ->
                file.isFile && normalizedExtensions.contains(file.extension)
            }
            .map { file ->
                val formattedSize = String.format("%.1fKb", file.length() / 1024.0)
                logger.info("${file.name} : ${formattedSize}")

                totalSize += file.length()
                totalCount++

                FileContent(file.absolutePath, file.readText())
            }
            .toList()
    }

    val formattedTotalSize = String.format("%.1fKb", totalSize / 1024.0)
    logger.info("TOTAL files: $totalCount size: ${formattedTotalSize}")

    return fileContents
}
