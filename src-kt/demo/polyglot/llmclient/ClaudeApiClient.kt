package demo.polyglot.llmclient

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

/** Implementation of `LlmApiClient` for interacting with the Claude API. */
class ClaudeApiClient : LlmApiClient {
    override fun prepareRequest(prompt: String, apiKey: String): Request {
        val requestBody = JSONObject().apply {
            put("model", "claude-2")  // Claude model version
            put("prompt", prompt)
            put("max_tokens_to_sample", 2_048)  // Limit the response length
        }

        return Request.Builder()
            .url("https://api.anthropic.com/v1/messages")
            .addHeader("Content-Type", "application/json")
            .addHeader("x-api-key", apiKey)
            .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
            .build()
    }

    override fun parseResponse(jsonResponse: JSONObject): String {
        return jsonResponse.getString("completion")
    }
}
