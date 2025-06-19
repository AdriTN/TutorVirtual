import json
import pytest
import httpx

from src.models import Theme
import src.api.routes.ai as ai_module


def insert_theme(db_session, name="Números naturales", description="Tema de prueba"):
    """
    Crea un Theme en la BBDD de prueba.
    """
    tema = Theme(name=name, description=description, subject_id=1)
    db_session.add(tema)
    db_session.commit()
    db_session.refresh(tema)
    return tema


@pytest.mark.parametrize("raise_exc,status_code", [
    (httpx.HTTPError("fail"), 502),
])
def test_ollama_http_error_bubbles_up(client, monkeypatch, raise_exc, status_code):
    # Simulamos que generate_with_ollama lanza HTTPError
    monkeypatch.setattr(ai_module, "generate_with_ollama",
                        lambda payload: (_ for _ in ()).throw(raise_exc))

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "hola"}]
    })
    assert resp.status_code == status_code
    assert "Ollama:" in resp.json()["detail"]


def test_invalid_json_response(client, monkeypatch):
    # Simulamos respuesta válida HTTP, pero content no es JSON
    monkeypatch.setattr(ai_module, "generate_with_ollama",
                        lambda payload: {"choices": [{"message": {"content": "no-json"}}]})

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "hola"}]
    })
    assert resp.status_code == 500
    assert resp.json()["detail"] == "Respuesta AI inválida"


def test_theme_not_found(client, monkeypatch):
    data = {
        "tema": "Otro tema",
        "enunciado": "Enunciado",
        "tipo": "respuesta corta",
        "dificultad": "fácil",
        "respuesta": "42",
        "explicacion": ""
    }
    monkeypatch.setattr(ai_module, "generate_with_ollama",
                        lambda payload: {"choices": [{"message": {"content": json.dumps(data)}}]})

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "hola"}]
    })
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Tema no encontrado"


def test_success_path(client, db_session, monkeypatch):
    # Primero creamos el tema en la BBDD de prueba
    tema = insert_theme(db_session, name="números naturales", description="desc")

    # Payload simulado correcto
    data = {
        "tema": "Números naturales",
        "enunciado": "¿Cuánto es 2+2?",
        "tipo": "respuesta corta",
        "dificultad": "fácil",
        "respuesta": "4",
        "explicacion": "Suma sencilla"
    }
    monkeypatch.setattr(ai_module, "generate_with_ollama",
                        lambda payload: {"choices": [{"message": {"content": json.dumps(data)}}]})

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "generar ejercicio"}]
    })
    assert resp.status_code == 200

    body = resp.json()
    # Validamos campos del response
    assert set(body.keys()) == {"id", "tema", "enunciado", "dificultad", "tipo", "explicacion"}
    assert body["tema"] == tema.name
    assert body["enunciado"] == data["enunciado"]
    assert body["tipo"] == data["tipo"]
    assert body["dificultad"] == data["dificultad"]
    assert body["explicacion"] == data["explicacion"]

    # Además debe haberse creado el Exercise en la BBDD
    from src.models import Exercise
    ej = db_session.query(Exercise).get(body["id"])
    assert ej is not None
    assert ej.answer == data["respuesta"]
