import uuid

import pytest
from fastapi import FastAPI, Request
from starlette.testclient import TestClient

from app.api.middlewares.request_id import RequestIDMiddleware

# Creamos una mini-app fastapi para probar el middleware
@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    # Montamos el middleware
    app.add_middleware(RequestIDMiddleware)

    @app.get("/ping")
    async def ping(request: Request):
        # Devolvemos el request_id que el middleware guardó en request.state
        return {"request_id": request.state.request_id}

    return TestClient(app)


def test_request_id_header_and_state(client: TestClient):
    # Hacemos la llamada
    response = client.get("/ping")
    # 1) Debemos tener el header X-Request-ID
    assert "X-Request-ID" in response.headers

    rid_header = response.headers["X-Request-ID"]
    # 2) El valor debe ser un UUID válido
    #    Esto lanzaría ValueError si no lo fuera
    parsed = uuid.UUID(rid_header)
    assert str(parsed) == rid_header

    # 3) El body devuelve el mismo request_id desde request.state
    body = response.json()
    assert body["request_id"] == rid_header


def test_request_id_changes_each_request(client: TestClient):
    # Primera petición
    r1 = client.get("/ping")
    # Segunda petición
    r2 = client.get("/ping")

    # Deben ser distintos
    assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]
