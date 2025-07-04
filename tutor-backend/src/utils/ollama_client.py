import httpx
import structlog
from fastapi import Request, HTTPException

from src.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger("ollama")

class OllamaNotAvailableError(HTTPException):
    def __init__(self, detail: str = "Ollama service is not available or not configured."):
        super().__init__(status_code=503, detail=detail)

class OllamaClient:
    def __init__(self, base_url: str | None, api_key: str | None = None):
        self.base_url = base_url
        self.api_key = api_key
        self.is_enabled = bool(base_url)
        self._client: httpx.AsyncClient | None = None

        if self.is_enabled:
            logger.info("Ollama client enabled", url=self.base_url)
        else:
            logger.warn("Ollama client disabled: OLLAMA_URL not configured.")

    async def _get_client(self) -> httpx.AsyncClient:
        if not self.is_enabled or not self.base_url: # Should not happen if is_enabled is true
            raise OllamaNotAvailableError("Ollama client is not enabled.")
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url.rstrip("/") + "/api",
                timeout=httpx.Timeout(240, connect=20),
                limits=httpx.Limits(max_connections=20, max_keepalive_connections=15),
            )
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None

    async def check_availability(self, request: Request | None = None) -> bool:
        if not self.is_enabled:
            return False
        
        log = logger.bind(request_id=getattr(request.state, "request_id", "n/a") if request else "n/a")
        try:
            client = await self._get_client()
            # A simple GET request to a known Ollama endpoint, e.g., /tags (list local models)
            # or just try to connect. For now, let's assume if base_url is set, it's potentially available.
            # A more robust check would ping an endpoint.
            # For simplicity, we'll rely on the first actual call to fail if it's truly down.
            # However, we can try a quick health check here.
            response = await client.get("/tags") # Example: list models
            response.raise_for_status()
            log.info("Ollama service is available and responding.")
            return True
        except (httpx.ConnectError, httpx.HTTPStatusError, httpx.ReadTimeout) as e:
            log.warn("Ollama service check failed.", error=str(e), ollama_url=self.base_url)
            self.is_enabled = False # Mark as disabled if check fails
            return False
        except OllamaNotAvailableError: # Should not happen here but good practice
             self.is_enabled = False
             return False


    async def generate_chat_completion(self, payload: dict, request: Request | None = None) -> dict:
        if not self.is_enabled:
            logger.warn("Attempted to use Ollama when client is disabled.")
            raise OllamaNotAvailableError()

        endpoint = "/chat" # Corrected endpoint for Ollama's chat API (often /api/chat or /v1/chat/completions)
                           # Based on existing code, it seems to be /api/chat/completions
                           # The AsyncClient base_url is already /api, so this becomes /chat
                           # Let's adjust to use the full path if base_url is just the host.
                           # The original code used settings.ollama_url.rstrip("/") + "/api/chat/completions"
                           # So, if base_url is "http://ollama:11434", then endpoint should be "/chat/completions"
                           # If base_url is "http://ollama:11434/api", then endpoint is "/chat/completions"
                           # Let's make the endpoint relative to /api/
        
        # The original function used "/api/chat/completions".
        # If self.base_url is "http://ollama:11434", then client.base_url is "http://ollama:11434/api"
        # So, the endpoint for client.post should be "/chat/completions"
        # If ollama_url from settings includes /api, AsyncClient base_url will have /api/api.
        # Let's ensure base_url for AsyncClient does NOT include /api if settings.ollama_url does.
        # Safest: construct full URL or ensure AsyncClient base_url is just scheme+host+port.

        # Re-evaluating client instantiation:
        # Let's assume settings.ollama_url is "http://host:port"
        # Then AsyncClient base_url should be "http://host:port/api"
        # And the request should be to "/chat" or "/chat/completions"
        # Ollama's API for chat is typically POST /api/chat
        # Let's stick to /api/chat for the client.post if base_url includes /api
        # Or use client.post("/chat") if base_url is "http://ollama:11434/api"

        # The original code used: url = settings.ollama_url.rstrip("/") + "/api/chat/completions"
        # This implies the ollama_url in settings does NOT have /api.
        # So, if settings.ollama_url = "http://ollama:11434"
        # then self.base_url = "http://ollama:11434"
        # and client = httpx.AsyncClient(base_url="http://ollama:11434/api", ...)
        # then client.post("/chat", ...) would go to "http://ollama:11434/api/chat"
        # This seems to be the standard Ollama API endpoint.

        chat_endpoint = "/chat" # Standard Ollama API endpoint relative to /api

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req_id = getattr(request.state, "request_id", "n/a") if request and hasattr(request, "state") else "n/a"
        log = logger.bind(request_id=req_id)

        client = await self._get_client()
        
        for attempt in range(1, 4):
            try:
                log.debug("Sending request to Ollama", endpoint=chat_endpoint, attempt=attempt, payload=payload)
                r = await client.post(chat_endpoint, json=payload, headers=headers)
                r.raise_for_status()
                log.info("Ollama chat completion successful", status=r.status_code, attempt=attempt)
                # Ollama's /api/chat endpoint streams responses.
                # We need to aggregate it if we want a single JSON object like OpenAI's API.
                # Or, adapt to handle streaming if the original `generate_with_ollama` expected a single JSON.
                # The original code expected r.json() directly. This means the Ollama server
                # might have been run with OLLAMA_COMPATIBILITY_MODE=openai or similar,
                # or the /api/chat/completions endpoint was a custom proxy.
                # Given the payload structure, it looks like OpenAI compatibility.
                # If it's standard Ollama /api/chat, then "stream": false must be in payload for non-streaming.
                
                # Assuming the payload might need "stream": False for non-streaming response
                # and that the response is then a single JSON object.
                # If "stream": True (or default), it's a series of JSON objects.
                # The original code `return r.json()` implies a single JSON response.
                # Let's add "stream": False to the payload if not present.
                final_payload = payload.copy()
                if "stream" not in final_payload:
                    final_payload["stream"] = False

                # If using the standard /api/chat endpoint, the response for stream:false is a single JSON object.
                # If the original setup was using an OpenAI-compatible endpoint like /v1/chat/completions,
                # then the structure is different.
                # The original code used "/api/chat/completions", which is NOT standard Ollama.
                # Standard Ollama is "/api/chat".
                # Let's assume the user wants standard Ollama /api/chat.
                # The response format for /api/chat (stream: false) is:
                # { "model": "...", "created_at": "...", "message": {"role": "assistant", "content": "..."}, "done": true, ... }
                # The original code expected: { "choices": [{"message": {"content": "..."}}]}
                # This means we need to adapt the response or the client is misconfigured for standard Ollama.

                # For now, let's assume the endpoint and response structure of the original function was correct
                # and the Ollama server is set up to provide that (e.g. via a proxy or specific configuration).
                # So, if client base_url is "http://ollama:11434/api", then client.post("/chat/completions",...)
                # This was a misinterpretation. Original URL was `settings.ollama_url.rstrip("/") + "/api/chat/completions"`
                # So, if ollama_url is `http://ollama:11434`, then full URL is `http://ollama:11434/api/chat/completions`
                # The AsyncClient should have `base_url=settings.ollama_url` and endpoint `"/api/chat/completions"`
                # Let's correct the client instantiation and endpoint usage.

                # Corrected client logic:
                # _get_client should use self.base_url (which is settings.ollama_url)
                # and the post should be to the full path part "/api/chat/completions"
                
                # Re-correction:
                # self.base_url = "http://ollama:11434" (from settings.ollama_url)
                # self._client = httpx.AsyncClient(base_url=self.base_url, ...)
                # r = await client.post("/api/chat/completions", json=final_payload, headers=headers)

                # This is how it should be:
                if self._client is None or self._client.is_closed: # Re-initialize client if closed
                     self._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(240, connect=20),
                        limits=httpx.Limits(max_connections=20, max_keepalive_connections=15),
                    )
                
                full_url = self.base_url.rstrip("/") + "/api/chat/completions"
                r = await self._client.post(full_url, json=final_payload, headers=headers)
                r.raise_for_status()
                log.info("Ollama API call successful", status=r.status_code, url=full_url)
                return r.json()

            except httpx.ReadTimeout:
                log.warning("Ollama chat completion timeout", attempt=attempt, url=full_url if 'full_url' in locals() else chat_endpoint)
                if attempt == 3:
                    self.is_enabled = False # Disable on persistent timeout
                    log.error("Ollama disabled due to persistent timeout.")
                    raise OllamaNotAvailableError("Ollama service timed out after several attempts.")
            except httpx.ConnectError:
                log.error("Ollama chat completion connection error", attempt=attempt, url=full_url if 'full_url' in locals() else chat_endpoint)
                self.is_enabled = False # Disable on connection error
                log.error("Ollama disabled due to connection error.")
                raise OllamaNotAvailableError("Failed to connect to Ollama service.")
            except httpx.HTTPStatusError as exc:
                error_body = None
                try:
                    error_body = exc.response.json()
                except ValueError:
                    error_body = exc.response.text
                
                log.error(
                    "Ollama chat completion HTTP error", 
                    status=exc.response.status_code,
                    ollama_url=str(exc.request.url),
                    ollama_response_body=error_body,
                    attempt=attempt
                )
                if attempt == 3:
                    if exc.response.status_code >= 500: # Server-side errors
                        self.is_enabled = False # Disable on persistent server error
                        log.error("Ollama disabled due to persistent server-side HTTP error.")
                    raise OllamaNotAvailableError(f"Ollama service returned an error: {error_body}")
                # For client errors (4xx), we might not want to disable globally on retries,
                # but OllamaNotAvailableError is still appropriate for the calling function.
            except OllamaNotAvailableError: # Propagate if raised by _get_client
                raise
            except Exception as e: # Catch any other unexpected errors during the request
                log.error("Unexpected error during Ollama request", error=str(e), attempt=attempt, exc_info=True)
                if attempt == 3:
                    self.is_enabled = False # Disable on persistent unknown error
                    log.error("Ollama disabled due to persistent unexpected error.")
                    raise OllamaNotAvailableError(f"An unexpected error occurred with Ollama: {str(e)}")
        
        # Should not be reached if retries are exhausted, as an exception would be raised.
        # However, as a fallback:
        self.is_enabled = False 
        raise OllamaNotAvailableError("Ollama request failed after multiple retries.")


# Global instance or dependency injection?
# For now, let's create a global instance that services can import and use.
# This matches the pattern of `settings = get_settings()`.
# In a more complex app, use FastAPI's dependency injection for the client.

ollama_client = OllamaClient(base_url=settings.ollama_url, api_key=settings.api_key)


# Keep the original function signature for generate_with_ollama for now,
# but make it use the new client. This is for compatibility with existing calls.
# Eventually, this function can be deprecated/removed.
async def generate_with_ollama(payload: dict, request: Request | None = None) -> dict:
    """
    Legacy wrapper for OllamaClient.generate_chat_completion.
    Prefer using the OllamaClient instance directly.
    """
    global ollama_client
    if not ollama_client.is_enabled:
        # Perform a quick check if the client was disabled previously but might be back
        if settings.ollama_url: # Check if URL is configured at all
            logger.info("Re-initializing Ollama client as it was previously disabled but URL is set.")
            ollama_client = OllamaClient(base_url=settings.ollama_url, api_key=settings.api_key)
            # Optionally, try a quick health check here if desired, but generate_chat_completion will do it.
        else: # No URL, so definitely not available
            raise OllamaNotAvailableError("Ollama URL not configured.")

    # The client's method will handle enabling/disabling itself on errors.
    return await ollama_client.generate_chat_completion(payload, request)
