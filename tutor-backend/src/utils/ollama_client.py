import httpx
import structlog
from fastapi import Request

from src.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger("ollama")

async def generate_with_ollama(payload: dict, request: Request | None = None) -> dict:
    url = settings.ollama_url.rstrip("/") + "/api/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"

    if request is not None and hasattr(request, "state"):
        req_id = getattr(request.state, "request_id", "n/a")
    else:
        req_id = "n/a"
    log = logger.bind(request_id=req_id)

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(240, connect=20),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=15),
    ) as client:
        for attempt in range(1, 4):
            try:
                r = await client.post(url, json=payload, headers=headers)
                r.raise_for_status()
                log.info("ollama_ok", status=r.status_code)
                return r.json()
            except httpx.ReadTimeout:
                log.warning("ollama_timeout", attempt=attempt)
                if attempt == 3:
                    raise
            except httpx.HTTPStatusError as exc:
                error_body = None
                try:
                    error_body = exc.response.json() # Intenta parsear como JSON
                except ValueError: # Si el cuerpo no es JSON válido
                    error_body = exc.response.text # Toma el texto plano
                
                log.error(
                    "ollama_error", 
                    status=exc.response.status_code,
                    ollama_url=str(exc.request.url),
                    ollama_response_body=error_body # Loguea el cuerpo de la respuesta
                )
                raise
