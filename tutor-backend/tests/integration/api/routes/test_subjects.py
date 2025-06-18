"""
Pruebas de integración para las rutas de *Subjects*.

El *conftest* global ya nos inyecta:

* TestClient → autenticado como `user_id = 1, is_admin = True`.
* Sesión de BBDD en memoria → `db_session`.
"""
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
)

from app.models import Subject, User

API = "/api/subjects"


# ───────────────────────── helpers ──────────────────────────
def _mk_subject(client, name: str, *, desc: str | None = None):
    body = {"name": name, **({"description": desc} if desc else {})}
    return client.post(API, json=body)


def _enroll(client, subj_id: int):
    return client.post(f"{API}/{subj_id}/enroll")


def _unenroll(client, subj_id: int):
    return client.delete(f"{API}/{subj_id}/unenroll")


# ───────────────────────── tests ────────────────────────────
def test_create_subject_ok(client, db_session):
    """
    ✔ Devuelve 201 y persiste el subject.
    """
    resp = _mk_subject(client, "Maths", desc="Álgebra y cálculo")
    assert resp.status_code == HTTP_201_CREATED
    data = resp.json()
    assert data == {"id": 1, "name": "Maths", "description": "Álgebra y cálculo"}

    # BBDD realmente contiene la fila
    assert db_session.query(Subject).count() == 1


def test_create_subject_duplicate(client, db_session):
    """
    ✔ Nombre repetido → 409 Conflict.
    """
    _mk_subject(client, "Physics")
    resp = _mk_subject(client, "Physics")
    assert resp.status_code == HTTP_409_CONFLICT
    assert db_session.query(Subject).count() == 1   # nada nuevo


def test_list_subjects(client):
    """
    ✔ GET /subjects devuelve todos los registros.
    """
    _mk_subject(client, "Art")
    _mk_subject(client, "History")
    resp = client.get(API)
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert names == {"Art", "History"}


def test_enroll_and_unenroll_flow(client, db_session):
    """
    ✔ Post /enroll asocia el subject al usuario.
    ✔ Delete /unenroll quita la relación y cursos huérfanos.
    """
    # Creamos usuario 1 en BBDD (conftest solo “finge” el payload JWT)
    user = User(id=1, username="test", email="t@t.com", password="x")
    db_session.add(user)
    subj = Subject(name="Bio")
    db_session.add(subj)
    db_session.commit()

    # --- enroll -------------------------------------------------
    resp = _enroll(client, subj.id)
    assert resp.status_code == HTTP_204_NO_CONTENT
    db_session.refresh(user)
    assert subj in user.subjects

    # idempotencia: segundo enrolamiento debe ser inofensivo
    assert _enroll(client, subj.id).status_code == HTTP_204_NO_CONTENT

    # --- unenroll ----------------------------------------------
    resp = _unenroll(client, subj.id)
    assert resp.status_code == HTTP_204_NO_CONTENT
    db_session.refresh(user)
    assert subj not in user.subjects

    # idempotencia de nuevo
    assert _unenroll(client, subj.id).status_code == HTTP_204_NO_CONTENT


def test_enroll_unenroll_subject_not_found(client):
    """
    ✔ Subject inexistente → 404.
    """
    assert _enroll(client, 999).status_code   == HTTP_404_NOT_FOUND
    assert _unenroll(client, 999).status_code == HTTP_404_NOT_FOUND
