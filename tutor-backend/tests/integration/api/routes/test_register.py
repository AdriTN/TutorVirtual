from starlette.status import (
    HTTP_201_CREATED,
    HTTP_409_CONFLICT,
    HTTP_422_UNPROCESSABLE_ENTITY,
)
from sqlalchemy.orm import Session

from src.models import User


# ───────────────── helpers ──────────────────────────────────────────────
def _count_users(db: Session) -> int:
    return db.query(User).count()


# ───────────────── tests ────────────────────────────────────────────────
def test_register_ok(client, db_session):
    """
    ✔ Crea un usuario nuevo y devuelve 201 con los campos esperados.
    """
    body = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "S3cretP@ss",
        "confirm_password": "S3cretP@ss",
    }

    resp = client.post("/api/auth/register", json=body)

    assert resp.status_code == HTTP_201_CREATED
    data = resp.json()
    assert set(data) == {"id", "username", "email"}
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"

    # En la BBDD hay exactamente 1 usuario y su password está hasheada
    assert _count_users(db_session) == 1
    row = db_session.query(User).first()
    assert row.password != body["password"]          # no se almacena en claro
    assert len(row.password) > 20                    # bcrypt hash


def test_register_duplicate_username(client, db_session):
    """
    ✔ Devuelve 409 si el *username* ya existe (aunque cambie el e-mail).
    """
    client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "bob@x.com", "password": "N0tSoWeakP@ss!!", "confirm_password": "N0tSoWeakP@ss!!"},
    )
    resp = client.post(
        "/api/auth/register",
        json={"username": "bob", "email": "nuevo@x.com", "password": "N0tSoWeakP@ss!!", "confirm_password": "N0tSoWeakP@ss!!"},
    )
    assert resp.status_code == HTTP_409_CONFLICT
    assert resp.json() == {"detail": "Ya existe un usuario con ese nombre o e-mail"}
    assert _count_users(db_session) == 1


def test_register_duplicate_email(client, db_session):
    """
    ✔ Devuelve 409 si el e-mail ya existe (aunque cambie el *username*).
    """
    client.post(
        "/api/auth/register",
        json={"username": "carl", "email": "carl@x.com", "password": "N0tSoWeakP@ss!!", "confirm_password": "N0tSoWeakP@ss!!"},
    )
    resp = client.post(
        "/api/auth/register",
        json={"username": "otro", "email": "carl@x.com", "password": "N0tSoWeakP@ss!!", "confirm_password": "N0tSoWeakP@ss!!"},
    )
    assert resp.status_code == HTTP_409_CONFLICT
    assert _count_users(db_session) == 1


def test_register_validation_error(client):
    """
    ✔ Campos inválidos → 422 (FastAPI / Pydantic).
    """
    resp = client.post(
        "/api/auth/register",
        json={"username": "ab", "email": "no-es-email", "password": "S3uperS3cretP@ss!!", "confirm_password": "S3uperS3cretP@ss!!"},
    )
    assert resp.status_code == HTTP_422_UNPROCESSABLE_ENTITY
