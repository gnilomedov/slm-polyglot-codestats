package demo.polyglot

import demo.polyglot.llmclient.ApiClientResolver
import demo.polyglot.llmclient.TextUtils
import okhttp3.OkHttpClient
import okhttp3.Protocol
import okhttp3.Response
import org.json.JSONObject
import org.slf4j.Logger
import org.slf4j.LoggerFactory
import java.io.IOException

/**
 * Represents the result of an AI query along with metadata.
 *
 * @property prompt The original prompt sent to the AI.
 * @property response The response received from the AI.
 * @property apiUrl The URL of the API used for the query.
 * @property responseTime The time taken to receive the response in milliseconds.
 */
data class QueryResult(
    val prompt: String,
    val response: String,
    val apiUrl: String,
    val responseTime: Long
)

private val logger: Logger = LoggerFactory.getLogger("LlmQueryExecutor")

/**
 * Executes a query to the specified AI API and returns the result.
 *
 * @param apiUrl The URL of the AI API to query.
 * @param apiKey The API key for authentication.
 * @param prompt The prompt to send to the AI.
 * @return A QueryResult object containing the response and metadata.
 * @throws IOException if there's an error in network communication.
 * @throws RuntimeException if the API returns an unsuccessful response.
 */
@Throws(IOException::class, RuntimeException::class)
fun executeQuery(apiUrl: String, apiKey: String, prompt: String): QueryResult {
    logger.info("Will query prompt with ${TextUtils.getTextStats(prompt)}")

    val apiClient = ApiClientResolver.getApiClient(apiUrl)
    val client = OkHttpClient()
    val request = apiClient.prepareRequest(prompt, apiKey)

    val (response, responseTime) = if (request.url.toString().startsWith(
            "http://local+interactive")) {
        val localInteractiveResponse = Response.Builder()
            .request(request)
            .protocol(Protocol.HTTP_1_1)
            .code(200) // HTTP 200 OK
            .message("OK")
            .build()
        localInteractiveResponse to 0L
    } else {
        val startTime = System.currentTimeMillis()
        logger.info("Will query: $apiUrl ...")
        val actualResponse = client.newCall(request).execute()
        val endTime = System.currentTimeMillis()
        actualResponse to (endTime - startTime)
    }

    return if (response.isSuccessful) {
        val jsonResponse = JSONObject(response.body?.string() ?: "{}")
        val aiResponse = apiClient.parseResponse(jsonResponse)
        logger.info("Query executed successfully. Response time: $responseTime ms")
        QueryResult(prompt, aiResponse, apiUrl, responseTime)
    } else {
        val errorMessage = "Error: ${response.code} - ${response.message}"
        logger.error(errorMessage)
        throw RuntimeException(errorMessage)
    }
}
