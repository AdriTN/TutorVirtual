from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock # Para mockear llamadas externas

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from starlette import status # Para los códigos de estado HTTP

import src.api.routes.auth as auth_module
from src.models import User, RefreshToken, UserProvider # Añadido UserProvider
from src.core.security import hash_password


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


# ------------- Google OAuth Tests ------------------

GOOGLE_AUTH_URL = "/api/auth/google"
MOCK_GOOGLE_ID_TOKEN = "mock_google_id_token_string"
MOCK_GOOGLE_USER_SUB = "google_user_subject_123"
MOCK_GOOGLE_USER_EMAIL = "testuser@gmail.com"

@patch(f"{auth_module.__name__}.google_id_token.verify_oauth2_token")
@patch(f"{auth_module.__name__}.requests.post")
def test_google_login_new_user(
    mock_requests_post: MagicMock,
    mock_verify_id_token: MagicMock,
    client: TestClient, 
    db_session: Session,
    monkeypatch
):
    # Configurar mocks
    mock_requests_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id_token": MOCK_GOOGLE_ID_TOKEN, "access_token": "google_access_token"}
    )
    mock_verify_id_token.return_value = {
        "iss": "https://accounts.google.com",
        "sub": MOCK_GOOGLE_USER_SUB,
        "email": MOCK_GOOGLE_USER_EMAIL,
        "email_verified": True,
        "name": "Test User",
    }
    monkeypatch.setattr(auth_module, "create_access_token", lambda uid, adm: f"jwt_for_{uid}")
    monkeypatch.setattr(auth_module, "create_refresh_token", lambda: "new_refresh_token_google")

    # Llamada al endpoint
    response = client.post(GOOGLE_AUTH_URL, json={"code": "mock_auth_code"})

    # Verificaciones
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["refresh_token"] == "new_refresh_token_google"

    # Verificar creación de usuario y UserProvider
    user = db_session.query(User).filter_by(email=MOCK_GOOGLE_USER_EMAIL).first()
    assert user is not None
    assert user.username == "testuser" # Derivado del email
    assert tokens["access_token"] == f"jwt_for_{user.id}"


    user_provider = db_session.query(UserProvider).filter_by(user_id=user.id, provider="google", provider_user_id=MOCK_GOOGLE_USER_SUB).first()
    assert user_provider is not None

    # Verificar que se guardó el refresh token
    rt = db_session.query(RefreshToken).filter_by(user_id=user.id, token="new_refresh_token_google").first()
    assert rt is not None

    mock_requests_post.assert_called_once()
    mock_verify_id_token.assert_called_once_with(
        MOCK_GOOGLE_ID_TOKEN,
        auth_module.google_requests.Request(),
        auth_module.settings.google_client_id,
        clock_skew_in_seconds=5
    )

@patch(f"{auth_module.__name__}.google_id_token.verify_oauth2_token")
@patch(f"{auth_module.__name__}.requests.post")
def test_google_login_existing_user(
    mock_requests_post: MagicMock,
    mock_verify_id_token: MagicMock,
    client: TestClient, 
    db_session: Session,
    monkeypatch
):
    # Pre-configurar usuario existente
    existing_user = insert_user(db_session, email=MOCK_GOOGLE_USER_EMAIL, username="existing_google_user")
    db_session.add(UserProvider(user_id=existing_user.id, provider="google", provider_user_id=MOCK_GOOGLE_USER_SUB))
    db_session.commit()
    
    initial_user_count = db_session.query(User).count()
    initial_provider_count = db_session.query(UserProvider).count()

    # Configurar mocks
    mock_requests_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id_token": MOCK_GOOGLE_ID_TOKEN, "access_token": "google_access_token"}
    )
    mock_verify_id_token.return_value = {
        "sub": MOCK_GOOGLE_USER_SUB,
        "email": MOCK_GOOGLE_USER_EMAIL,
        "email_verified": True,
    }
    monkeypatch.setattr(auth_module, "create_access_token", lambda uid, adm: f"jwt_for_{uid}")
    monkeypatch.setattr(auth_module, "create_refresh_token", lambda: "another_refresh_token")

    # Llamada al endpoint
    response = client.post(GOOGLE_AUTH_URL, json={"code": "mock_auth_code"})

    # Verificaciones
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert tokens["access_token"] == f"jwt_for_{existing_user.id}"
    assert tokens["refresh_token"] == "another_refresh_token"

    assert db_session.query(User).count() == initial_user_count # No se crea nuevo usuario
    assert db_session.query(UserProvider).count() == initial_provider_count # No se crea nuevo provider

@patch(f"{auth_module.__name__}.requests.post")
def test_google_login_exchange_code_fails(mock_requests_post: MagicMock, client: TestClient):
    mock_requests_post.return_value = MagicMock(
        status_code=400,
        text="{\"error\":\"invalid_grant\",\"error_description\":\"Bad Request\"}",
        json=lambda: {"error": "invalid_grant", "error_description": "Bad Request"}
    )
    response = client.post(GOOGLE_AUTH_URL, json={"code": "invalid_code"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Error al intercambiar código con Google" in response.json()["detail"]["message"]
    assert response.json()["detail"]["google_error"] == "invalid_grant"

@patch(f"{auth_module.__name__}.requests.post")
def test_google_login_no_id_token_from_google(mock_requests_post: MagicMock, client: TestClient):
    mock_requests_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"access_token": "google_access_token"} # Falta id_token
    )
    response = client.post(GOOGLE_AUTH_URL, json={"code": "valid_code"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Respuesta de Google no incluyó 'id_token'."

@patch(f"{auth_module.__name__}.google_id_token.verify_oauth2_token")
@patch(f"{auth_module.__name__}.requests.post")
def test_google_login_id_token_verification_fails(
    mock_requests_post: MagicMock,
    mock_verify_id_token: MagicMock,
    client: TestClient
):
    mock_requests_post.return_value = MagicMock(
        status_code=200,
        json=lambda: {"id_token": "some_id_token", "access_token": "google_access_token"}
    )
    mock_verify_id_token.side_effect = ValueError("Token verification failed")
    
    response = client.post(GOOGLE_AUTH_URL, json={"code": "valid_code"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "id_token inválido o no verificado."
