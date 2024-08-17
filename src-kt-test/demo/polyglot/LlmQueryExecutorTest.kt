package demo.polyglot

import io.mockk.*
import java.io.IOException
import okhttp3.*
import okhttp3.Call
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.ResponseBody.Companion.toResponseBody
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test

import demo.polyglot.llmclient.ApiClientResolver
import demo.polyglot.llmclient.LlmApiClient
import demo.polyglot.llmclient.TextUtils

/** Tests for LlmQueryExecutor. */
class LlmQueryExecutorTest {
    private lateinit var mockApiClient: LlmApiClient
    private lateinit var mockCall: Call

    /**
     * Sets up the test environment before each test.
     *
     * This method mocks necessary objects and sets up common behavior
     * for the mocked objects used across multiple tests.
     */
    @BeforeEach
    fun setUp() {
        mockkObject(ApiClientResolver)
        mockkConstructor(OkHttpClient::class)
        mockkObject(TextUtils)

        mockApiClient = mockk()
        mockCall = mockk()

        every { TextUtils.getTextStats(any()) } returns "stats"
        every { anyConstructed<OkHttpClient>().newCall(any()) } returns mockCall
    }

    @AfterEach
    fun tearDown() {
        unmockkAll()
    }

    /** Data class to hold common test parameters. */
    data class TestParams(
        val apiUrl: String,
        val apiKey: String = "test-api-key",
        val prompt: String = "Test prompt"
    )

    /** Sets up common mocks for the given test parameters and request. */
    private fun setupCommonMocks(params: TestParams, mockRequest: Request) {
        every { ApiClientResolver.getApiClient(params.apiUrl) } returns mockApiClient
        every { mockApiClient.prepareRequest(params.prompt, params.apiKey) } returns mockRequest
    }

    @Test
    fun `executeQuery successful response`() {
        // Given
        val params = TestParams("https://api.example.com")
        val mockRequest = Request.Builder().url(params.apiUrl).build()
        setupCommonMocks(params, mockRequest)

        val responseBody = """{"response": "AI response"}"""
        val mockResponse = Response.Builder()
            .request(mockRequest)
            .protocol(Protocol.HTTP_1_1)
            .code(200)
            .message("OK")
            .body(responseBody.toResponseBody("application/json".toMediaType()))
            .build()

        every { mockApiClient.parseResponse(any()) } returns "AI response"
        every { mockCall.execute() } returns mockResponse

        // When
        val result = executeQuery(params.apiUrl, params.apiKey, params.prompt)

        // Then
        assertEquals(params.prompt, result.prompt)
        assertEquals("AI response", result.response)
        assertEquals(params.apiUrl, result.apiUrl)
        assertTrue(result.responseTime >= 0)

        verifyCommonCalls(params)
    }

    @Test
    fun `executeQuery local interactive response`() {
        // Given
        val params = TestParams("http://local+interactive")
        val mockRequest = Request.Builder().url(params.apiUrl).build()
        setupCommonMocks(params, mockRequest)

        every { mockApiClient.parseResponse(any()) } returns "Local interactive response"

        // When
        val result = executeQuery(params.apiUrl, params.apiKey, params.prompt)

        // Then
        assertEquals(params.prompt, result.prompt)
        assertEquals("Local interactive response", result.response)
        assertEquals(params.apiUrl, result.apiUrl)
        assertEquals(0L, result.responseTime)

        verify {
            ApiClientResolver.getApiClient(params.apiUrl)
            mockApiClient.prepareRequest(params.prompt, params.apiKey)
            mockApiClient.parseResponse(any())
            TextUtils.getTextStats(params.prompt)
        }
    }

    @Test
    fun `executeQuery unsuccessful response`() {
        // Given
        val params = TestParams("https://api.example.com")
        val mockRequest = Request.Builder().url(params.apiUrl).build()
        setupCommonMocks(params, mockRequest)

        val mockResponse = Response.Builder()
            .request(mockRequest)
            .protocol(Protocol.HTTP_1_1)
            .code(400)
            .message("Bad Request")
            .body("Error".toResponseBody("text/plain".toMediaType()))
            .build()

        every { mockCall.execute() } returns mockResponse

        // When/Then
        val exception = assertThrows(RuntimeException::class.java) {
            executeQuery(params.apiUrl, params.apiKey, params.prompt)
        }
        assertEquals("Error: 400 - Bad Request", exception.message)

        verifyCommonCalls(params)
    }

    @Test
    fun `executeQuery throws IOException`() {
        // Given
        val params = TestParams("https://api.example.com")
        val mockRequest = Request.Builder().url(params.apiUrl).build()
        setupCommonMocks(params, mockRequest)

        every { mockCall.execute() } throws IOException("Network error")

        // When/Then
        assertThrows(IOException::class.java) {
            executeQuery(params.apiUrl, params.apiKey, params.prompt)
        }

        verifyCommonCalls(params)
    }

    /** Verifies common method calls for all tests. */
    private fun verifyCommonCalls(params: TestParams) {
        verify {
            ApiClientResolver.getApiClient(params.apiUrl)
            mockApiClient.prepareRequest(params.prompt, params.apiKey)
            TextUtils.getTextStats(params.prompt)
            anyConstructed<OkHttpClient>().newCall(any())
            mockCall.execute()
        }
    }
}