"""
Pruebas del CRUD mínimo de temas (/api/themes).
La ruta POST está protegida por admin_required, pero conftest
ya la parchea para que todos los tests sean admin.
"""
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_204_NO_CONTENT,
)

from src.models import Subject, Theme
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

# Helper para crear un tema directamente en la BD para los tests de PUT/DELETE
def _create_theme_direct_db(db_session: Session, name: str, subject_id: int, description: str | None = "Test Desc") -> Theme:
    theme = Theme(name=name, description=description, subject_id=subject_id)
    db_session.add(theme)
    db_session.commit()
    db_session.refresh(theme)
    return theme


# ───────────────── helpers ──────────────────────────────
def _make_subject(db, name="Math"):
    subj = Subject(name=name)
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


# ───────────────── tests ────────────────────────────────
def test_create_theme_ok(client, db_session):
    """
    ✔ Devuelve 201 y persiste el tema cuando subject existe y no hay duplicados.
    """
    subj = _make_subject(db_session)

    body = {"name": "Fracciones", "description": "Operaciones básicas", "subject_id": subj.id} # Corregido aquí
    resp = client.post("/api/themes", json=body)

    assert resp.status_code == HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Fracciones"
    assert data["description"] == "Operaciones básicas"
    assert "id" in data

    theme_in_db = db_session.query(Theme).filter_by(id=data["id"]).first()
    assert theme_in_db is not None
    assert theme_in_db.name == "Fracciones"
    assert theme_in_db.description == "Operaciones básicas"


def test_create_theme_duplicate_name(client, db_session):
    """
    ✔ name duplicado → 409 CONFLICT.
    """
    subj = _make_subject(db_session)
    db_session.add(Theme(name="Geometría", subject_id=subj.id))
    db_session.commit()

    resp = client.post("/api/themes", json={"name": "Geometría", "subject_id": subj.id})

    assert resp.status_code == HTTP_409_CONFLICT
    assert resp.json() == {"detail": "Duplicado: Ya existe un tema con ese nombre"} # Corregido aquí


def test_create_theme_subject_not_found(client):
    """
    ✔ Subject inexistente → 404 NOT FOUND.
    """
    resp = client.post("/api/themes", json={"name": "Óptica", "subject_id": 999})
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Asignatura con ID 999 no encontrada"} # Corregido aquí


def test_create_theme_missing_name(client, db_session):
    """
    ✔ Falta name → 422 UNPROCESSABLE ENTITY.
    """
    subj = _make_subject(db_session)
    resp = client.post("/api/themes", json={"descripcion": "Sin nombre", "subject_id": subj.id})
    assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    # Pydantic v2 style error
    assert resp.json()["detail"][0]["type"] == "missing"
    assert resp.json()["detail"][0]["loc"] == ["body", "name"]


def test_create_theme_missing_subject_id(client):
    """
    ✔ Falta subject_id → 422 UNPROCESSABLE ENTITY.
    """
    resp = client.post("/api/themes", json={"name": "Tema Huérfano"})
    assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"][0]["type"] == "missing"
    assert resp.json()["detail"][0]["loc"] == ["body", "subject_id"]


def test_create_theme_invalid_subject_id_type(client):
    """
    ✔ subject_id con tipo incorrecto → 422 UNPROCESSABLE ENTITY.
    """
    resp = client.post("/api/themes", json={"name": "Tema Inválido", "subject_id": "no-un-numero"})
    assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"][0]["type"] == "int_parsing"
    assert resp.json()["detail"][0]["loc"] == ["body", "subject_id"]


def test_create_theme_name_too_long(client, db_session):
    """
    ✔ name demasiado largo → 422 UNPROCESSABLE ENTITY.
    """
    subj = _make_subject(db_session)
    long_name = "a" * 256
    resp = client.post("/api/themes", json={"name": long_name, "subject_id": subj.id})
    assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
    assert resp.json()["detail"][0]["type"] == "string_too_long"
    assert resp.json()["detail"][0]["loc"] == ["body", "name"]
    assert resp.json()["detail"][0]["ctx"]["max_length"] == 255


def test_list_all_themes(client, db_session):
    """
    ✔ GET /api/themes devuelve todos los temas existentes.
    """
    subj = _make_subject(db_session, "Historia")
    db_session.add_all(
        [
            Theme(name="Edad Media", subject_id=subj.id),
            Theme(name="Edad Moderna", subject_id=subj.id),
        ]
    )
    db_session.commit()

    resp = client.get("/api/themes")
    assert resp.status_code == HTTP_200_OK

    names = {item["title"] for item in resp.json()}
    assert names == {"Edad Media", "Edad Moderna"}


# ───────────────── PUT /api/themes/{theme_id} ────────────────────────────────
def test_update_theme_ok(client: TestClient, db_session: Session):
    """
    ✔ Actualiza nombre, descripción y subject_id de un tema existente.
    """
    subject1 = _make_subject(db_session, name="Matemáticas")
    subject2 = _make_subject(db_session, name="Física")
    theme = _create_theme_direct_db(db_session, name="Algebra", subject_id=subject1.id, description="Desc Original")

    update_data = {
        "name": "Algebra Lineal",
        "description": "Nueva Descripción",
        "subject_id": subject2.id,
    }
    resp = client.put(f"/api/themes/{theme.id}", json=update_data)

    assert resp.status_code == HTTP_200_OK
    data = resp.json()
    assert data["name"] == "Algebra Lineal"
    assert data["description"] == "Nueva Descripción"
    assert data["subject_id"] == subject2.id

    db_session.refresh(theme)
    assert theme.name == "Algebra Lineal"
    assert theme.description == "Nueva Descripción"
    assert theme.subject_id == subject2.id


def test_update_theme_partial(client: TestClient, db_session: Session):
    """
    ✔ Actualiza solo algunos campos de un tema.
    """
    subject1 = _make_subject(db_session, name="Química")
    theme = _create_theme_direct_db(db_session, name="Orgánica", subject_id=subject1.id, description="Desc Antigua")

    update_data = {"name": "Química Orgánica"}
    resp = client.put(f"/api/themes/{theme.id}", json=update_data)

    assert resp.status_code == HTTP_200_OK
    data = resp.json()
    assert data["name"] == "Química Orgánica"
    assert data["description"] == "Desc Antigua" # No debe cambiar
    assert data["subject_id"] == subject1.id    # No debe cambiar

    db_session.refresh(theme)
    assert theme.name == "Química Orgánica"
    assert theme.description == "Desc Antigua"


def test_update_theme_not_found(client: TestClient):
    """
    ✔ Devuelve 404 si el tema a actualizar no existe.
    """
    resp = client.put("/api/themes/999", json={"name": "Inexistente"})
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Tema no encontrado"


def test_update_theme_duplicate_name(client: TestClient, db_session: Session):
    """
    ✔ Devuelve 409 si el nuevo nombre del tema ya existe en otro tema.
    """
    subject1 = _make_subject(db_session, name="Lengua")
    _create_theme_direct_db(db_session, name="Sintaxis", subject_id=subject1.id)
    theme_to_update = _create_theme_direct_db(db_session, name="Ortografía", subject_id=subject1.id)

    resp = client.put(f"/api/themes/{theme_to_update.id}", json={"name": "Sintaxis"})
    assert resp.status_code == HTTP_409_CONFLICT
    assert resp.json()["detail"] == "Ya existe otro tema con ese nombre"


def test_update_theme_target_subject_not_found(client: TestClient, db_session: Session):
    """
    ✔ Devuelve 404 si el subject_id al que se quiere mover el tema no existe.
    """
    subject1 = _make_subject(db_session, name="Biología")
    theme = _create_theme_direct_db(db_session, name="Célula", subject_id=subject1.id)

    resp = client.put(f"/api/themes/{theme.id}", json={"subject_id": 999}) # subject_id 999 no existe
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Asignatura destino con ID 999 no encontrada"


# ───────────────── DELETE /api/themes/{theme_id} ─────────────────────────────
def test_delete_theme_ok(client: TestClient, db_session: Session):
    """
    ✔ Elimina un tema existente y devuelve 204.
    """
    subject1 = _make_subject(db_session, name="Geografía")
    theme = _create_theme_direct_db(db_session, name="Ríos", subject_id=subject1.id)

    resp = client.delete(f"/api/themes/{theme.id}")
    assert resp.status_code == HTTP_204_NO_CONTENT

    deleted_theme = db_session.query(Theme).get(theme.id)
    assert deleted_theme is None


def test_delete_theme_not_found(client: TestClient):
    """
    ✔ Devuelve 404 si el tema a eliminar no existe.
    """
    resp = client.delete("/api/themes/999")
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json()["detail"] == "Tema no encontrado"
