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
        
        # Ensure payload includes "stream": false for OpenAI-compatible non-streaming response
        final_payload = payload.copy()
        if "stream" not in final_payload:
            final_payload["stream"] = False

        # Construct the target URL for Open WebUI's OpenAI-compatible endpoint
        # self.base_url is expected to be like "http://open-webui:8080/ollama"
        target_openai_endpoint = "/api/chat/completions"
        full_url = self.base_url.rstrip("/") + target_openai_endpoint
        
        for attempt in range(1, 4):
            try:
                # Initialize or get the client instance
                # We will use one client instance for the retries of this specific request.
                # This client is initialized without a base_url, so full_url must be used.
                if self._client is None or self._client.is_closed:
                    self._client = httpx.AsyncClient(
                        timeout=httpx.Timeout(240, connect=20),
                        limits=httpx.Limits(max_connections=20, max_keepalive_connections=15),
                    )
                
                log.debug(
                    "Attempting OpenAI-compatible chat completion with Open WebUI", 
                    url=full_url, 
                    attempt=attempt, 
                    model=final_payload.get("model")
                )
                
                r = await self._client.post(full_url, json=final_payload, headers=headers)
                r.raise_for_status() # Raises HTTPStatusError for 4xx/5xx responses

                log.info(
                    "OpenAI-compatible chat completion successful via Open WebUI", 
                    status=r.status_code, 
                    url=full_url,
                    attempt=attempt
                )
                return r.json() # Expecting OpenAI response structure: {"choices": [...]}

            except httpx.ReadTimeout:
                log.warning("Open WebUI chat completion timeout", attempt=attempt, url=full_url if 'full_url' in locals() else "api/chat/completions")
                if attempt == 3:
                    self.is_enabled = False # Disable on persistent timeout
                    log.error("Open WebUI disabled due to persistent timeout.")
                    raise OllamaNotAvailableError("Open WebUI service timed out after several attempts.")
            except httpx.ConnectError:
                log.error("Open WebUI chat completion connection error", attempt=attempt, url=full_url if 'full_url' in locals() else "api/chat/completions")
                self.is_enabled = False # Disable on connection error
                log.error("Open WebUI disabled due to connection error.")
                raise OllamaNotAvailableError("Failed to connect to Ollama service.")
            except httpx.HTTPStatusError as exc:
                error_body = None
                try:
                    error_body = exc.response.json()
                except ValueError:
                    error_body = exc.response.text
                
                log.error(
                    "Open WebUI chat completion HTTP error", 
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
