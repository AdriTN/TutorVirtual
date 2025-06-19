import pytest
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.api.dependencies.auth import jwt_required, admin_required
import src.api.dependencies.auth as auth_dep

@pytest.fixture(autouse=True)
def clear_decode_token(monkeypatch):
    # nos aseguramos de que decode_token no haga nada real
    monkeypatch.setattr(auth_dep, "decode_token", lambda token: None)
    yield

def make_creds(token: str) -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)

class DummyPayload(dict):
    pass

def test_jwt_required_missing_token():
    # Sin credenciales → 401 Missing token
    with pytest.raises(HTTPException) as exc:
        jwt_required(credentials=None)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Missing token" in str(exc.value.detail)

def test_jwt_required_invalid_token(monkeypatch):
    # Credenciales presentes pero decode_token devuelve None → 401 Invalid or expired
    creds = make_creds("whatever")
    # ya viene parcheado para devolver None
    with pytest.raises(HTTPException) as exc:
        jwt_required(credentials=creds)
    assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Invalid or expired token" in str(exc.value.detail)

def test_jwt_required_valid_token(monkeypatch):
    # Token válido → devuelve el payload
    expected = DummyPayload(user_id=42, is_admin=False)
    monkeypatch.setattr(auth_dep, "decode_token", lambda token: expected)
    creds = make_creds("good-token")
    out = jwt_required(credentials=creds)
    assert out is expected

def test_admin_required_non_admin(monkeypatch):
    # Payload sin is_admin → 403
    payload = DummyPayload(user_id=1, is_admin=False)
    monkeypatch.setattr(auth_dep, "decode_token", lambda token: payload)
    creds = make_creds("t")
    # Primero invocamos jwt_required para obtener el payload
    p = jwt_required(credentials=creds)
    with pytest.raises(HTTPException) as exc:
        # admin_required espera el payload como dependency
        admin_required(payload=p)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Admin privileges required" in str(exc.value.detail)

def test_admin_required_admin(monkeypatch):
    # Payload con is_admin=True → pasa
    payload = DummyPayload(user_id=1, is_admin=True)
    # directamente llamamos admin_required
    out = admin_required(payload=payload)
    assert out is payload
