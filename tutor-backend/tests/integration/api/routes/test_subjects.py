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

API = "/api/subjects"        # prefijo común


# ───────────────────────── helpers ──────────────────────────
def _mk_subject(client, name: str, *, desc: str | None = None):
    """POST /api/subjects/nueva (description es obligatoria)."""
    if desc is None:                     # proveemos una por defecto
        desc = f"{name} desc"
    body = {"name": name, "description": desc}
    return client.post(f"{API}/nueva", json=body)


def _enroll(client, subj_id: int):
    return client.post(f"{API}/{subj_id}/enroll")


def _unenroll(client, subj_id: int):
    return client.delete(f"{API}/{subj_id}/unenroll")


# ───────────────────────── tests ────────────────────────────
def test_create_subject_ok(client, db_session):
    """✔ Devuelve 201 y persiste el subject."""
    resp = _mk_subject(client, "Maths", desc="Álgebra y cálculo")
    assert resp.status_code == HTTP_201_CREATED
    assert resp.json() == {
        "id": 1,
        "name": "Maths",
        "description": "Álgebra y cálculo",
    }
    assert db_session.query(Subject).count() == 1


def test_create_subject_duplicate(client, db_session):
    """✔ Nombre repetido → 409 Conflict."""
    _mk_subject(client, "Physics", desc="Física clásica")
    resp = _mk_subject(client, "Physics", desc="Física clásica")
    assert resp.status_code == HTTP_409_CONFLICT
    assert db_session.query(Subject).count() == 1


def test_list_subjects(client):
    """✔ GET /subjects devuelve todos los registros."""
    _mk_subject(client, "Art", desc="Historia del arte")
    _mk_subject(client, "History", desc="Historia universal")
    resp = client.get(f"{API}/subjects")
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert names == {"Art", "History"}


def test_enroll_and_unenroll_flow(client, db_session):
    """
    ✔ POST /enroll asocia el subject al usuario.
    ✔ DELETE /unenroll quita la relación y cursos huérfanos.
    """
    user = User(id=1, username="test", email="t@t.com", password="x")
    subj = Subject(name="Bio", description="Biología")
    db_session.add_all([user, subj])
    db_session.commit()

    assert _enroll(client, subj.id).status_code == HTTP_204_NO_CONTENT
    db_session.refresh(user)
    assert subj in user.subjects

    assert _enroll(client, subj.id).status_code == HTTP_204_NO_CONTENT

    assert _unenroll(client, subj.id).status_code == HTTP_204_NO_CONTENT
    db_session.refresh(user)
    assert subj not in user.subjects

    assert _unenroll(client, subj.id).status_code == HTTP_204_NO_CONTENT


def test_enroll_unenroll_subject_not_found(client):
    """✔ Subject inexistente → 404."""
    assert _enroll(client, 999).status_code   == HTTP_404_NOT_FOUND
    assert _unenroll(client, 999).status_code == HTTP_404_NOT_FOUND
