package demo.polyglot.llmclient

import okhttp3.Request
import org.json.JSONObject

interface LlmApiClient {
    /**
     * Prepares an HTTP request for the LLM API.
     * @param prompt The input text to be processed by the LLM.
     * @param apiKey The authentication key for the API.
     * @return A Request object ready to be sent to the LLM API.
     */
    fun prepareRequest(prompt: String, apiKey: String): Request

    /**
     * Parses the JSON response from the LLM API.
     * @param jsonResponse The JSON response from the API.
     * @return The extracted text response from the LLM.
     */
    fun parseResponse(jsonResponse: JSONObject): String
}
