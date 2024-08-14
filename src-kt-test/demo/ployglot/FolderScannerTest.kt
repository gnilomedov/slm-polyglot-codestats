package demo.polyglot

import io.mockk.*
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.assertEquals
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import java.io.File

/** Tests for FolderScanner class. */
class FolderScannerTest {
    @BeforeEach
    fun setUp() {
        mockkStatic(File::class)
        mockkStatic(File::extension)
        mockkStatic(File::readText)
        mockkStatic(File::walk)
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    @Test
    fun `scanFolders filter single extension read content`() {
        // Given
        createMockFileTreeWalk(
            listOf(
                "/test/foo" to createMockFile("/test/foo", "test_code", "cpp", "Foo .cpp"),
                "/test/bar" to createMockFile("/test/bar", "test_code", "py", "Bar .py")
            )
        )

        // When
        val fileContents = scanFolders(listOf("/test/foo", "/test/bar"), listOf(".cpp"))

        // Then
        assertEquals(1, fileContents.size)
        assertEquals("/test/foo/test_code.cpp", fileContents[0].path)
        assertEquals("Foo .cpp", fileContents[0].content)
    }

    @Test
    fun `scanFolders filter multiple extensions read content`() {
        // Given
        createMockFileTreeWalk(
            listOf(
                "/test/foo" to createMockFile("/test/foo", "test_code", "cpp", "Foo .cpp"),
                "/test/bar" to createMockFile("/test/bar", "test_code", "py", "Bar .py")
            )
        )

        // When
        val fileContents = scanFolders(listOf("/test/foo", "/test/bar"), listOf(".cpp", ".py"))

        // Then
        assertEquals(2, fileContents.size)
        assertEquals("/test/foo/test_code.cpp", fileContents[0].path)
        assertEquals("Foo .cpp", fileContents[0].content)
        assertEquals("/test/bar/test_code.py", fileContents[1].path)
        assertEquals("Bar .py", fileContents[1].content)
    }

    /** Creates a mock File object with specified properties. */
    private fun createMockFile(
        dirPath: String,
        name: String,
        extension: String,
        content: String
    ): File =
        mockk<File>(relaxed = true).apply {
            every { this@apply.isFile } returns true
            every { this@apply.name } returns "$name.$extension"
            every { this@apply.extension } returns extension
            every { this@apply.absolutePath } returns "$dirPath/$name.$extension"
            every { this@apply.readText() } returns content
        }

    /** Creates a mock FileTreeWalk for given directory paths and mock files. */
    private fun createMockFileTreeWalk(dirPathAndMockFiles: List<Pair<String, File>>) =
        dirPathAndMockFiles.groupBy { it.first }.forEach { (dirPath, files) ->
            every { File(dirPath).walk() } returns mockk<FileTreeWalk> {
                every { /*FileTreeWalk*/ iterator() } returns files.map { it.second }.iterator()
            }
        }
}
