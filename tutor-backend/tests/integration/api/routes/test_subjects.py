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
    HTTP_409_CONFLICT,
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
)
from sqlalchemy import select, and_

from src.models import Subject, User, Course # Añadido Course
from src.models.associations import user_enrollments, course_subjects, user_courses # Añadidas tablas de asociación

API = "/api/subjects"        # prefijo común


# ───────────────────────── helpers ──────────────────────────
def _mk_subject(client, name: str, *, desc: str | None = None):
    """POST /api/subjects/create (description es obligatoria)."""
    if desc is None:                     # proveemos una por defecto
        desc = f"{name} desc"
    body = {"name": name, "description": desc}
    return client.post(f"{API}/create", json=body)

# Modificado para incluir course_id
def _enroll(client, subj_id: int, course_id: int):
    return client.post(f"{API}/{subj_id}/enroll", json={"course_id": course_id})

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
    resp = client.get(f"{API}/all")
    assert resp.status_code == 200
    names = {s["name"] for s in resp.json()}
    assert names == {"Art", "History"}


def test_enroll_unenroll_resource_not_found(client, db_session):
    """✔ Subject o Course inexistente durante matriculación/desmatriculación → 404."""
    
    # Crear un curso y una asignatura válidos para los tests
    valid_course_resp = client.post("/api/courses", json={"title": "Curso Valido Test", "description": "Desc"})
    assert valid_course_resp.status_code == 201 # Asumiendo que el cliente es admin por conftest
    valid_course_id = valid_course_resp.json()["id"]

    valid_subject_resp = _mk_subject(client, "Asignatura Valida Test", desc="Desc")
    assert valid_subject_resp.status_code == HTTP_201_CREATED
    valid_subject_id = valid_subject_resp.json()["id"]

    # Caso 1: Subject ID inválido, Course ID válido
    assert _enroll(client, 999, valid_course_id).status_code == HTTP_404_NOT_FOUND

    # Caso 2: Subject ID válido, Course ID inválido
    assert _enroll(client, valid_subject_id, 999).status_code == HTTP_404_NOT_FOUND
    
    # Caso 3: Ambos IDs inválidos
    assert _enroll(client, 888, 999).status_code == HTTP_404_NOT_FOUND # Probablemente falle en subject primero
