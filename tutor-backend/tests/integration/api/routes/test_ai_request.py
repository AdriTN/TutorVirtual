import json
import pytest
import httpx

from src.models import Theme
import src.api.routes.ai as ai_module


from src.models import Subject # Importar Subject

def insert_subject_for_ai(db_session, name="Matemáticas IA", description="Asignatura para IA tests"):
    subject = db_session.query(Subject).filter_by(name=name).first()
    if not subject:
        subject = Subject(name=name, description=description)
        db_session.add(subject)
        db_session.commit()
        db_session.refresh(subject)
    return subject

def insert_theme(db_session, name="Números naturales", description="Tema de prueba", subject_id=None):
    """
    Crea un Theme en la BBDD de prueba.
    Si subject_id no se proporciona, crea/usa una asignatura por defecto.
    """
    if subject_id is None:
        default_subject = insert_subject_for_ai(db_session)
        subject_id = default_subject.id
        
    tema = Theme(name=name, description=description, subject_id=subject_id)
    db_session.add(tema)
    db_session.commit()
    db_session.refresh(tema)
    return tema


@pytest.mark.parametrize("raise_exc,status_code", [
    (httpx.HTTPError("fail"), 502),
])
def test_ollama_http_error_bubbles_up(client, monkeypatch, raise_exc, status_code):
    # Simulamos que generate_with_ollama lanza HTTPError
    async def mock_generate_with_ollama_http_error(payload):
        raise raise_exc
    monkeypatch.setattr(ai_module, "generate_with_ollama", mock_generate_with_ollama_http_error)

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "hola"}]
    })
    assert resp.status_code == status_code
    assert "Ollama:" in resp.json()["detail"]


def test_invalid_json_response(client, monkeypatch):
    # Simulamos respuesta válida HTTP, pero content no es JSON
    async def mock_generate_with_ollama_invalid_json(payload):
        return {"choices": [{"message": {"content": "no-json"}}]}
    monkeypatch.setattr(ai_module, "generate_with_ollama", mock_generate_with_ollama_invalid_json)

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
    async def mock_generate_with_ollama_theme_not_found(payload):
        return {"choices": [{"message": {"content": json.dumps(data)}}]}
    monkeypatch.setattr(ai_module, "generate_with_ollama", mock_generate_with_ollama_theme_not_found)

    resp = client.post("/api/ai/request", json={
        "model": "m",
        "response_format": {},
        "messages": [{"role": "user", "content": "hola"}]
    })
    assert resp.status_code == 404
    assert resp.json()["detail"] == f"Tema '{data.get('tema', 'N/A')}' no encontrado"


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
    async def mock_generate_with_ollama_success(payload):
        return {"choices": [{"message": {"content": json.dumps(data)}}]}
    monkeypatch.setattr(ai_module, "generate_with_ollama", mock_generate_with_ollama_success)

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
