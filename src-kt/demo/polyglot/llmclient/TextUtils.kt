package demo.polyglot.llmclient

object TextUtils {
    fun getTextStats(text: String): String =
        "lines: ${text.lines().size} " +
        "words: ${text.split("\\s+".toRegex()).filter { it.isNotEmpty() }.size} " +
        "chars: ${text.length}"
}
