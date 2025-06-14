import httpx
import structlog
from fastapi import Request

from ..core.config import get_settings

settings = get_settings()
logger = structlog.get_logger("ollama")

def generate_with_ollama(payload: dict, request: Request | None = None) -> dict:
    url = settings.ollama_url.rstrip("/") + "/api/chat/completions"
    headers = {"Content-Type": "application/json"}
    if settings.ollama_api_key:
        headers["Authorization"] = f"Bearer {settings.ollama_api_key}"

    log = logger.bind(request_id=getattr(request.state, "request_id", "n/a"))

    with httpx.Client(
        timeout=httpx.Timeout(120, connect=10),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    ) as client:
        for attempt in range(1, 4):
            try:
                r = client.post(url, json=payload, headers=headers)
                r.raise_for_status()
                log.info("ollama_ok", status=r.status_code)
                return r.json()
            except httpx.ReadTimeout:
                log.warning("ollama_timeout", attempt=attempt)
                if attempt == 3:
                    raise
            except httpx.HTTPStatusError as exc:
                log.error("ollama_error", status=exc.response.status_code)
                raise
