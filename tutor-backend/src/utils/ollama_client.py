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
        if not self.is_enabled or not self.base_url:
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
            response = await client.get("/tags")
            response.raise_for_status()
            log.info("Ollama service is available and responding.")
            return True
        except (httpx.ConnectError, httpx.HTTPStatusError, httpx.ReadTimeout) as e:
            log.warn("Ollama service check failed.", error=str(e), ollama_url=self.base_url)
            self.is_enabled = False
            return False
        except OllamaNotAvailableError:
             self.is_enabled = False
             return False


    async def generate_chat_completion(self, payload: dict, request: Request | None = None) -> dict:
        if not self.is_enabled:
            logger.warn("Attempted to use Ollama when client is disabled.")
            raise OllamaNotAvailableError()

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req_id = getattr(request.state, "request_id", "n/a") if request and hasattr(request, "state") else "n/a"
        log = logger.bind(request_id=req_id)
        
        final_payload = payload.copy()
        if "stream" not in final_payload:
            final_payload["stream"] = False

        target_openai_endpoint = "/api/chat/completions"
        full_url = self.base_url.rstrip("/") + target_openai_endpoint
        
        for attempt in range(1, 4):
            try:
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
                r.raise_for_status()

                log.info(
                    "OpenAI-compatible chat completion successful via Open WebUI", 
                    status=r.status_code, 
                    url=full_url,
                    attempt=attempt
                )
                return r.json()

            except httpx.ReadTimeout:
                log.warning("Open WebUI chat completion timeout", attempt=attempt, url=full_url if 'full_url' in locals() else "api/chat/completions")
                if attempt == 3:
                    self.is_enabled = False
                    log.error("Open WebUI disabled due to persistent timeout.")
                    raise OllamaNotAvailableError("Open WebUI service timed out after several attempts.")
            except httpx.ConnectError:
                log.error("Open WebUI chat completion connection error", attempt=attempt, url=full_url if 'full_url' in locals() else "api/chat/completions")
                self.is_enabled = False
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
                    if exc.response.status_code >= 500:
                        self.is_enabled = False
                        log.error("Ollama disabled due to persistent server-side HTTP error.")
                    raise OllamaNotAvailableError(f"Ollama service returned an error: {error_body}")
            except OllamaNotAvailableError:
                raise
            except Exception as e:
                log.error("Unexpected error during Ollama request", error=str(e), attempt=attempt, exc_info=True)
                if attempt == 3:
                    self.is_enabled = False
                    log.error("Ollama disabled due to persistent unexpected error.")
                    raise OllamaNotAvailableError(f"An unexpected error occurred with Ollama: {str(e)}")
        
        self.is_enabled = False 
        raise OllamaNotAvailableError("Ollama request failed after multiple retries.")


ollama_client = OllamaClient(base_url=settings.ollama_url, api_key=settings.api_key)


async def generate_with_ollama(payload: dict, request: Request | None = None) -> dict:
    """
    Legacy wrapper for OllamaClient.generate_chat_completion.
    Prefer using the OllamaClient instance directly.
    """
    global ollama_client
    if not ollama_client.is_enabled:
        if settings.ollama_url:
            logger.info("Re-initializing Ollama client as it was previously disabled but URL is set.")
            ollama_client = OllamaClient(base_url=settings.ollama_url, api_key=settings.api_key)
        else:
            raise OllamaNotAvailableError("Ollama URL not configured.")

    return await ollama_client.generate_chat_completion(payload, request)
