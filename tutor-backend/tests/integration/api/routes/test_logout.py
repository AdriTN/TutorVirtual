"""
Pruebas de la ruta   POST /auth/logout

El *conftest* suministra:
* `client`        – TestClient con la dependencia get_db apuntando a la BBDD
                    en memoria y jwt_required → user_id = 1
* `db_session`    – sesión de SQLAlchemy inyectada en la app
"""
from datetime import datetime, timedelta, timezone

from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND
from sqlalchemy.orm import Session

from app.models import RefreshToken


# ───────── helpers ──────────────────────────────────────────────────────────
def _insert_refresh(db: Session, *, token: str, user_id: int = 1):
    """Crea un refresh-token válido para el usuario indicado."""
    row = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(row)
    db.commit()
    return row


# ───────── tests ────────────────────────────────────────────────────────────
def test_logout_ok(client, db_session):
    """
    ✔ Devuelve 204 y elimina el token cuando pertenece al usuario autenticado.
    """
    _insert_refresh(db_session, token="abcdefghij", user_id=1)

    resp = client.post("/api/auth/logout", json={"refresh_token": "abcdefghij"})

    assert resp.status_code == HTTP_204_NO_CONTENT
    assert resp.content == b""
    assert db_session.query(RefreshToken).count() == 0


def test_logout_token_not_found(client):
    """
    ✔ Devuelve 404 si el token no existe en BBDD.
    """
    resp = client.post("/api/auth/logout", json={"refresh_token": "inexistente"})
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert resp.json() == {"detail": "Token no encontrado"}


def test_logout_not_owned_token(client, db_session):
    """
    ✔ Devuelve 404 si el token existe pero pertenece a **otro** usuario.
    Protege contra intento de borrado ajeno.
    """
    _insert_refresh(db_session, token="xyzfijepky", user_id=2)   # distinto user_id

    resp = client.post("/api/auth/logout", json={"refresh_token": "xyzfijepky"})
    assert resp.status_code == HTTP_404_NOT_FOUND
    assert (
        db_session.query(RefreshToken).filter_by(token="xyzfijepky").count() == 1
    ), "El token ajeno no debe eliminarse"
