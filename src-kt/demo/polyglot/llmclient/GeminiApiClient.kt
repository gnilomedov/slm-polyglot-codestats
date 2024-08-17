package demo.polyglot.llmclient

import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

/** Implementation of `LlmApiClient` for interacting with the Gemini API. */
class GeminiApiClient : LlmApiClient {
    override fun prepareRequest(prompt: String, apiKey: String): Request {
        val requestBody = JSONObject().apply {
            put("contents", listOf(
                JSONObject().apply {
                    put("parts", listOf(
                        JSONObject().apply {
                            put("text", prompt)
                        }
                    ))
                }
            ))
            put("generationConfig", JSONObject().apply {
                put("temperature", 0.7)  // Controls randomness (0.0 to 1.0)
                put("topK", 40)          // Limits vocabulary for next token selection
                put("topP", 0.95)        // Nucleus sampling probability threshold
                put("maxOutputTokens", 2_048)  // Limits the response length
            })
        }

        return Request.Builder()
            .url("https://generativelanguage.googleapis.com/" +
                    "v1beta/models/gemini-pro:generateContent?key=$apiKey")
            .addHeader("Content-Type", "application/json")
            .post(requestBody.toString().toRequestBody("application/json".toMediaType()))
            .build()
    }

    override fun parseResponse(jsonResponse: JSONObject): String {
        return jsonResponse.getJSONArray("candidates")
            .getJSONObject(0)
            .getJSONObject("content")
            .getJSONArray("parts")
            .getJSONObject(0)
            .getString("text")
    }
}
