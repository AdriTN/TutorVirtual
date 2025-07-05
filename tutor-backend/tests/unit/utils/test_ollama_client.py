import os

# ——————————————————————————————————————————————————————————————————————————————————————————
# Antes de importar anything que use get_settings(), configuramos las ENV vars
# ——————————————————————————————————————————————————————————————————————————————————————————
os.environ.update({
    "DATABASE_URL": "postgresql://user:password@localhost/testdb",
    "JWT_SECRET": "a" * 32,
    "GOOGLE_CLIENT_ID":     "test-google-client-id",
    "GOOGLE_CLIENT_SECRET": "test-google-client-secret",
    "OLLAMA_URL": "http://localhost:11434",
})

import httpx
import pytest
from types import SimpleNamespace
from fastapi import Request

from src.utils.ollama_client import generate_with_ollama, settings


class DummyRequest:
    def __init__(self, request_id: str):
        self.state = SimpleNamespace(request_id=request_id)


class DummyResponse:
    def __init__(self, status_code: int, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("HTTP error", request=None, response=self)


class AsyncDummyClientFactory:  # Renombrado y adaptado para async
    def __init__(self, *args, responses):
        self._responses = list(responses)

    async def __aenter__(self): # Context manager asíncrono
        return self

    async def __aexit__(self, exc_type, exc, tb): # Context manager asíncrono
        return False

    async def post(self, url, json, headers): # Método post asíncrono
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.fixture(autouse=True)
def no_real_http(monkeypatch):
    # Bloquea cualquier httpx.AsyncClient no mockeado
    async def mock_error_client(*args, **kwargs):
        raise RuntimeError("httpx.AsyncClient no mockeado en este test")
    
    monkeypatch.setattr(
        httpx,
        "AsyncClient",  # Mockear AsyncClient
        mock_error_client
    )
    yield


async def test_success(monkeypatch): # Convertido a async
    payload = {"foo": "bar"}
    expected = {"reply": "ok"}

    resp = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "AsyncClient",  # Mockear AsyncClient
        lambda *args, **kwargs: AsyncDummyClientFactory(responses=[resp])
    )

    out = await generate_with_ollama(payload, request=DummyRequest("req-1")) # Añadido await
    assert out == expected


async def test_timeout_then_success(monkeypatch): # Convertido a async
    payload = {"q": "test"}
    expected = {"answer": 42}

    resp_ok = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "AsyncClient",  # Mockear AsyncClient
        lambda *args, **kwargs: AsyncDummyClientFactory(
            responses=[
                httpx.ReadTimeout("timeout"),
                httpx.ReadTimeout("timeout"),
                resp_ok,
            ]
        )
    )

    out = await generate_with_ollama(payload, request=DummyRequest("req-2")) # Añadido await
    assert out == expected


async def test_http_status_error_bubbles_up(monkeypatch): # Convertido a async
    payload = {"hello": "world"}

    resp_500 = DummyResponse(500)
    monkeypatch.setattr(
        httpx,
        "AsyncClient",  # Mockear AsyncClient
        lambda *args, **kwargs: AsyncDummyClientFactory(responses=[resp_500])
    )

    with pytest.raises(httpx.HTTPStatusError):
        await generate_with_ollama(payload, request=DummyRequest("req-3")) # Añadido await


async def test_authorization_header(monkeypatch): # Convertido a async
    payload = {"x": "y"}
    expected = {"ok": True}

    # Forzamos que settings.api_key esté presente
    settings.api_key = "secret-token"

    captured = {}

    class CaptureClient(AsyncDummyClientFactory): # Hereda de AsyncDummyClientFactory
        async def post(self, url, json, headers): # Convertido a async
            captured["headers"] = headers
            return await super().post(url, json, headers) # Usa await

    resp = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "AsyncClient", # Mockear AsyncClient
        lambda *args, **kwargs: CaptureClient(responses=[resp])
    )

    out = await generate_with_ollama(payload, request=None) # Añadido await
    assert out == expected
    assert "Authorization" in captured["headers"]
    assert captured["headers"]["Authorization"] == f"Bearer {settings.api_key}"


async def test_no_api_key_header(monkeypatch):
    payload = {"z": "w"}

    settings.api_key = None

    captured = {}

    class CaptureClient(AsyncDummyClientFactory): # Hereda de AsyncDummyClientFactory
        async def post(self, url, json, headers): # Convertido a async
            captured["headers"] = headers.copy()
            # No es necesario llamar a super() si siempre devuelve una nueva DummyResponse
            return DummyResponse(200, json_data={"foo": "bar"})

    monkeypatch.setattr(
        httpx,
        "AsyncClient", # Mockear AsyncClient
        lambda *args, **kwargs: CaptureClient(responses=[DummyResponse(200, {"foo": "bar"})])
    )

    out = await generate_with_ollama(payload) # Añadido await
    assert out == {"foo": "bar"}
    assert "Authorization" not in captured["headers"]
