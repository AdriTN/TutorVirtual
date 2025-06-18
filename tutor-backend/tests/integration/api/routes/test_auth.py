from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

import src.app.api.routes.auth as auth_module
from app.models import User, RefreshToken
from app.core.security import hash_password


# ------------- helpers ----------------
def insert_user(db: Session, *, email="ada@example.com",
                password="Str0ng!Pass1", username=None, is_admin=False) -> User:
    """Devuelve un User existente o lo crea si no está."""
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user

    if username is None:
        username = email.split("@")[0]

    user = User(
        username=username,
        email=email,
        password=hash_password(password),
        is_admin=is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def insert_refresh(db: Session, user: User,
                   *, minutes=30) -> RefreshToken:
    token = "rt_" + ("x" * 30)          # no importa su forma, sólo unicidad
    rt = RefreshToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=minutes),
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    return rt


# ------------- tests ------------------
def test_login_invalid_credentials(client: TestClient, db_session: Session):
    insert_user(db_session, email="ada@example.com",
                password="Str0ng!Pass1")

    data = {"email": "ada@example.com", "password": "WRONG"}
    r = client.post("/api/auth/login", json=data)

    assert r.status_code == 400
    assert r.json()["detail"] == "Credenciales inválidas"


def test_login_ok_generates_tokens(client: TestClient, db_session: Session,
                                   monkeypatch):
    user = insert_user(db_session)

    # Evitamos depender de librerías de JWT – mockeamos creadores
    monkeypatch.setattr(auth_module, "create_access_token",
                        lambda uid, adm: f"jwt_for_{uid}")
    monkeypatch.setattr(auth_module, "create_refresh_token",
                        lambda: "refresh_token")

    data = {"email": user.email, "password": "Str0ng!Pass1"}
    r = client.post("/api/auth/login", json=data)

    assert r.status_code == 200
    assert r.json() == {"access_token": "jwt_for_%s" % user.id,
                        "refresh_token": "refresh_token"}

    # refresh_token debe haberse guardado en BBDD
    assert db_session.query(RefreshToken).count() == 1


def test_refresh_token_invalid(client: TestClient):
    r = client.post("/api/auth/refresh",
                    json={"refresh_token": "does_not_exist"})
    assert r.status_code == 400
    assert r.json()["detail"] == "Token inválido"


def test_refresh_token_expired(client: TestClient, db_session: Session):
    user = insert_user(db_session)
    rt = insert_refresh(db_session, user, minutes=-1)   # pasado

    r = client.post("/api/auth/refresh",
                    json={"refresh_token": rt.token})

    # Token caducado
    assert r.status_code == 400
    assert r.json()["detail"] == "Token expirado"


def test_refresh_rotates_and_returns_new_tokens(client, db_session,
                                                monkeypatch):
    user = insert_user(db_session)
    old_rt = insert_refresh(db_session, user, minutes=30)

    monkeypatch.setattr(auth_module, "create_access_token",
                        lambda uid, adm: "new_access")
    monkeypatch.setattr(auth_module, "create_refresh_token",
                        lambda: "new_refresh")

    r = client.post("/api/auth/refresh",
                    json={"refresh_token": old_rt.token})

    assert r.status_code == 200
    assert r.json() == {"access_token": "new_access",
                        "refresh_token": "new_refresh"}

    # El token anterior debe haberse sustituido
    db_session.refresh(old_rt)
    assert old_rt.token == "new_refresh"
