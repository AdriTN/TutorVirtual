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

from app.utils.ollama_client import generate_with_ollama, settings


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


class DummyClientFactory:
    def __init__(self, *args, responses):
        self._responses = list(responses)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, json, headers):
        resp = self._responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


@pytest.fixture(autouse=True)
def no_real_http(monkeypatch):
    # Bloquea cualquier httpx.Client no mockeado
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            RuntimeError("httpx.Client no mockeado en este test")
        )
    )
    yield


def test_success(monkeypatch):
    payload = {"foo": "bar"}
    expected = {"reply": "ok"}

    resp = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: DummyClientFactory(responses=[resp])
    )

    out = generate_with_ollama(payload, request=DummyRequest("req-1"))
    assert out == expected


def test_timeout_then_success(monkeypatch):
    payload = {"q": "test"}
    expected = {"answer": 42}

    resp_ok = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: DummyClientFactory(
            responses=[
                httpx.ReadTimeout("timeout"),
                httpx.ReadTimeout("timeout"),
                resp_ok,
            ]
        )
    )

    out = generate_with_ollama(payload, request=DummyRequest("req-2"))
    assert out == expected


def test_http_status_error_bubbles_up(monkeypatch):
    payload = {"hello": "world"}

    resp_500 = DummyResponse(500)
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: DummyClientFactory(responses=[resp_500])
    )

    with pytest.raises(httpx.HTTPStatusError):
        generate_with_ollama(payload, request=DummyRequest("req-3"))


def test_authorization_header(monkeypatch):
    payload = {"x": "y"}
    expected = {"ok": True}

    # Forzamos que settings.api_key esté presente
    settings.api_key = "secret-token"

    captured = {}

    class CaptureClient(DummyClientFactory):
        def post(self, url, json, headers):
            captured["headers"] = headers
            return super().post(url, json, headers)

    resp = DummyResponse(200, json_data=expected)
    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: CaptureClient(responses=[resp])
    )

    out = generate_with_ollama(payload, request=None)
    assert out == expected
    assert "Authorization" in captured["headers"]
    assert captured["headers"]["Authorization"] == f"Bearer {settings.api_key}"


def test_no_api_key_header(monkeypatch):
    payload = {"z": "w"}

    settings.api_key = None

    captured = {}

    class CaptureClient(DummyClientFactory):
        def post(self, url, json, headers):
            captured["headers"] = headers.copy()
            return DummyResponse(200, json_data={"foo": "bar"})

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda *args, **kwargs: CaptureClient(responses=[DummyResponse(200, {"foo": "bar"})])
    )

    out = generate_with_ollama(payload)
    assert out == {"foo": "bar"}
    assert "Authorization" not in captured["headers"]
