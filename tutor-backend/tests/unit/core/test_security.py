import pytest
import jwt
import uuid
from datetime import datetime, timedelta, timezone

import app.core.security as sec

class DummySettings:
    jwt_secret = "x" * 32
    jwt_algorithm = "HS256"
    jwt_access_minutes = 2
    bcrypt_rounds = 4

@pytest.fixture(autouse=True)
def parchear_config(monkeypatch):
    """
    Sustituye get_settings() para devolver DummySettings,
    de modo que las funciones lean esta configuración fija.
    """
    monkeypatch.setattr(sec, "get_settings", lambda: DummySettings())
    yield

def test_hash_and_verify_correct_password():
    pwd = "Secreto123!"
    hashed = sec.hash_password(pwd)
    assert sec.verify_password(pwd, hashed) is True

def test_verify_wrong_password():
    hashed = sec.hash_password("OtraClave!")
    assert sec.verify_password("NoEsLaClave", hashed) is False

def test_create_access_token_and_decode_token():
    # Creamos un token de acceso
    token = sec.create_access_token(user_id=42, is_admin=True)
    # Lo decodificamos manualmente con PyJWT
    decoded = jwt.decode(
        token,
        DummySettings.jwt_secret,
        algorithms=[DummySettings.jwt_algorithm],
        options={"verify_exp": False}
    )
    assert decoded["user_id"] == 42
    assert decoded["is_admin"] is True

    # Y a través de nuestra función decode_token()
    assert sec.decode_token(token)["user_id"] == 42

def test_decode_invalid_token_returns_none():
    assert sec.decode_token("token-que-no-es-jwt") is None

def test_decode_expired_token_returns_none():
    # Generamos un payload ya expirado
    payload = {
        "user_id": 1,
        "is_admin": False,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1)
    }
    expired_token = jwt.encode(
        payload,
        DummySettings.jwt_secret,
        algorithm=DummySettings.jwt_algorithm
    )
    assert sec.decode_token(expired_token) is None

def test_create_refresh_token_has_entropy_and_uniqueness():
    tok1 = sec.create_refresh_token()
    tok2 = sec.create_refresh_token()

    assert isinstance(tok1, str)
    assert isinstance(tok2, str)

    # token_urlsafe(32) → ≥ 43 caracteres base64-url
    assert len(tok1) >= 43
    assert len(tok2) >= 43

    # nunca deben coincidir
    assert tok1 != tok2
