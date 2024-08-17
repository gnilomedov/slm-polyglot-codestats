package demo.polyglot.llmclient

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

/** Implementation of `LlmApiClient` for interacting with the Open AI API. */
class OpenAiApiClient : LlmApiClient {
    override fun prepareRequest(prompt: String, apiKey: String): Request {
        val requestBody = JSONObject().apply {
            put("model", "gpt-3.5-turbo")  // Specify the GPT model version
            put("messages", listOf(
                JSONObject().put("role", "system")
                    .put("content", "You are a helpful assistant that improves Kotlin code."),
                JSONObject().put("role", "user").put("content", prompt)
            ))
            put("max_tokens", 2_048)  // Limit the response length
        }

        return Request.Builder()
            .url("https://api.openai.com/v1/chat/completions")
            .addHeader("Content-Type", "application/json")
            .addHeader("Authorization", "Bearer $apiKey")
            .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
            .build()
    }

    override fun parseResponse(jsonResponse: JSONObject): String {
        return jsonResponse.getJSONArray("choices")
            .getJSONObject(0)
            .getJSONObject("message")
            .getString("content")
    }
}
