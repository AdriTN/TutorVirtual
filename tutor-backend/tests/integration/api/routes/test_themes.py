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
)

from src.models import Subject, Theme


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

    body = {"name": "Fracciones", "descripcion": "Operaciones básicas", "subject_id": subj.id}
    resp = client.post("/api/themes", json=body)

    assert resp.status_code == HTTP_201_CREATED
    data = resp.json()
    assert data["name"] == "Fracciones"

    assert db_session.query(Theme).filter_by(id=data["id"]).count() == 1


def test_create_theme_duplicate_name(client, db_session):
    """
    ✔ name duplicado → 409 CONFLICT.
    """
    subj = _make_subject(db_session)
    db_session.add(Theme(name="Geometría", subject_id=subj.id))
    db_session.commit()

    resp = client.post("/api/themes", json={"name": "Geometría", "subject_id": subj.id})

    assert resp.status_code == HTTP_409_CONFLICT
    assert resp.json() == {"detail": "Duplicado"}


def test_create_theme_subject_not_found(client):
    """
    ✔ Subject inexistente → 404 NOT FOUND.
    """
    resp = client.post("/api/themes", json={"name": "Óptica", "subject_id": 999})
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Subject no encontrado"}


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
