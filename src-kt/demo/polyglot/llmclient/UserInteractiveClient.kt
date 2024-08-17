package demo.polyglot.llmclient

import java.awt.Toolkit
import java.awt.datatransfer.DataFlavor
import java.awt.datatransfer.StringSelection
import java.util.*
import okhttp3.Request
import org.json.JSONObject
import org.slf4j.LoggerFactory

/**
 * Implements LlmApiClient for interactive user input/output.
 * This client transfers prompts to the user and receives responses
 * through various methods including system clipboard and standard I/O.
 */
class UserInteractiveClient : LlmApiClient {
    private val logger = LoggerFactory.getLogger(UserInteractiveClient::class.java)

    /** Prepares a request by transferring the prompt to the user and creating a dummy request. */
    override fun prepareRequest(prompt: String, apiKey: String): Request {
        logger.info("Will query prompt with ${TextUtils.getTextStats(prompt)}")
        transferPromptToUser(prompt)
        return Request.Builder().url("http://local+interactive").build()
    }

    /** Parses the response by receiving input from the user. */
    override fun parseResponse(jsonResponse: JSONObject): String {
        println("\nPress Enter when you're ready to paste your response.")
        Scanner(System.`in`).nextLine()
        return receiveResponseFromUser().also {
            logger.info("Received response with ${TextUtils.getTextStats(it)}")
        }
    }

    private fun transferPromptToUser(prompt: String) {
        when {
            transferUsingAwt(prompt) -> return
            transferUsingXclip(prompt) -> return
            else -> transferUsingStdout(prompt)
        }
    }

    private fun receiveResponseFromUser(): String =
        receiveUsingAwt() ?: receiveUsingXclip() ?: receiveUsingStdin()

    /** Attempts transfer via AWT system clipboard. */
    private fun transferUsingAwt(txt: String): Boolean = try {
        logger.info("Transfer via AWT systemClipboard ...")
        Toolkit.getDefaultToolkit().systemClipboard.setContents(StringSelection(txt), null)
        logger.info("Transfer via AWT systemClipboard ... Done.\nPrompt text is in your clipboard.")
        true
    } catch (e: Throwable) {
        logger.error("Transfer via AWT systemClipboard ... ${e.message}")
        false
    }

    /** Attempts transfer via AWT xclip command. */
    private fun transferUsingXclip(txt: String): Boolean = try {
        logger.info("Transfer via xclip ...")
        Runtime.getRuntime().exec(arrayOf("xclip", "-selection", "clipboard")).apply {
            outputStream.use { it.write(txt.toByteArray()) }
            waitFor()
        }
        logger.info("Transfer via xclip ... Done.\nPrompt text is in your clipboard.")
        true
    } catch (e: Throwable) {
        logger.error("Transfer via xclip ... ${e.message}")
        false
    }

    /** Transfers the prompt by printing it to stdout. */
    private fun transferUsingStdout(txt: String): Boolean {
        println("\n\n\nPrompt:\n\n''' ''' '''\n\n$txt\n\n''' ''' '''\n\n")
        return true
    }

    /** Attempts to receive via AWT system clipboard. */
    private fun receiveUsingAwt(): String? = try {
        logger.info("Receive via AWT systemClipboard ...")
        (Toolkit.getDefaultToolkit().systemClipboard.getData(DataFlavor.stringFlavor) as String).also {
            logger.info("Receive via AWT systemClipboard ... Done.")
        }
    } catch (e: Throwable) {
        logger.error("Receive via AWT systemClipboard ... ${e.message}")
        null
    }

    /** Attempts to receive via xclip command. */
    private fun receiveUsingXclip(): String? = try {
        logger.info("Receive via xclip...")
        Runtime.getRuntime().exec(arrayOf("xclip", "-selection", "clipboard", "-o")).let { process ->
            process.inputStream.bufferedReader().use { reader -> reader.readText() }.also {
                process.waitFor()
                logger.info("Receive via xclip successful.")
            }
        }
    } catch (e: Throwable) {
        logger.error("Receive via xclip ... ${e.message}")
        null
    }

    /** Receives the response by reading from stdin. */
    private fun receiveUsingStdin(): String {
        println("Please enter your response. Type two empty lines to finish:")
        return buildString {
            var emptyLines = 0
            Scanner(System.`in`).use { scanner ->
                while (emptyLines < 2) {
                    val line = scanner.nextLine()
                    if (line.isEmpty()) emptyLines++ else {
                        emptyLines = 0
                        appendLine(line)
                    }
                }
            }
        }.trim()
    }
}
