from datetime import datetime, timedelta, timezone
import secrets

import jwt
from passlib.context import CryptContext

from src.core.config import get_settings

# Creamos el contexto de bcrypt sólo una vez
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashea con bcrypt la contraseña en claro.
    """
    return _pwd.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    """
    Verifica que `password` coincide con el hash.
    """
    return _pwd.verify(password, hashed)


def _expiry(minutes: int) -> datetime:
    """
    Devuelve la fecha UTC actual + minutos.
    """
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)


def create_access_token(user_id: int, is_admin: bool) -> str:
    """
    Genera un JWT de acceso con los claims:
      - user_id, is_admin
      - exp calculado según configuración
    """
    cfg = get_settings()
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": _expiry(cfg.jwt_access_minutes),
    }
    return jwt.encode(payload, cfg.jwt_secret, algorithm=cfg.jwt_algorithm)


def decode_token(token: str, secret: str | None = None) -> dict | None:
    """
    Decodifica un JWT. Si se pasa `secret`, se usa ese en lugar del de configuración.
    - Si está expirado → propaga jwt.ExpiredSignatureError
    - Si falla por otro motivo → devuelve None
    """
    cfg = get_settings()

    try:
        return jwt.decode(token, cfg.jwt_secret, algorithms=[cfg.jwt_algorithm])
    except jwt.PyJWTError:
        # Token mal formado, firma inválida distinta de expirado, etc.
        return None


def create_refresh_token() -> str:
    """
    Genera un UUID4 como token de refresco.
    """
    return secrets.token_urlsafe(32)
