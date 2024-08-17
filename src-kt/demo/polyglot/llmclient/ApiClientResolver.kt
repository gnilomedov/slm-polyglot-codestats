package demo.polyglot.llmclient

object ApiClientResolver {
    /**
     * Retrieves an instance of `LlmApiClient` based on the provided API URL.
     *
     * The URL "http://local+interactive" is treated as a special case that handles user interaction
     * rather than API calls.
     *
     * @param apiUrl The URL of the API for which the client is to be obtained.
     * @return An instance of the appropriate `LlmApiClient` implementation.
     * @throws IllegalArgumentException if the `apiUrl` does not match any supported patterns.
     */
    fun getApiClient(apiUrl: String): LlmApiClient {
        return when {
            apiUrl.startsWith("http://local+interactive") -> UserInteractiveClient()
            apiUrl.startsWith("https://generativelanguage.googleapis.com") -> GeminiApiClient()
            apiUrl.startsWith("https://api.openai.com") -> OpenAiApiClient()
            apiUrl.startsWith("https://api.anthropic.com") -> ClaudeApiClient()
            else -> throw IllegalArgumentException("Unsupported API URL")
        }
    }
}
