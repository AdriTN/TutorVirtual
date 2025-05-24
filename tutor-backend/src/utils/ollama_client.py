import httpx
import logging
from ..config import settings

logger = logging.getLogger(__name__)

def generate_with_ollama(payload: dict) -> dict:
    """
    Llama a Ollama/OpenWebUI en local. 
    Usa URL de env OLLAMA_URL y endpoint /api/chat/completions.
    Reintenta hasta 3 veces ante timeout.
    """
    # Construye la URL correcta:
    endpoint = "/api/chat/completions"
    url = settings.ollama_url.rstrip("/") + endpoint

    headers: dict[str,str] = {
        "Content-Type": "application/json",
    }
    if settings.api_key:
        headers["Authorization"] = f"Bearer {settings.api_key}"

    with httpx.Client(
        timeout=httpx.Timeout(60.0, connect=10.0),
        limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
    ) as client:
        for attempt in range(1, 4):
            try:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                return resp.json()
            except httpx.ReadTimeout:
                logger.warning("Timeout en intento %d de llamada a Ollama", attempt)
                if attempt == 3:
                    raise
            except httpx.HTTPStatusError as e:
                # capturamos 4xx/5xx
                logger.error("Ollama devolvió %d: %s", e.response.status_code, e.response.text)
                raise
    # no debería llegar aquí
