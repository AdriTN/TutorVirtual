from datetime import datetime, timedelta, timezone
from typing import Annotated
import uuid

import jwt
from passlib.context import CryptContext

from .config import get_settings

_cfg = get_settings()
_pwd = CryptContext(schemes=["bcrypt"], bcrypt__rounds=_cfg.bcrypt_rounds)

Algorithm = Annotated[str, "JWT algorithm"]

def hash_password(password: str) -> str:
    return _pwd.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return _pwd.verify(password, hashed)

def _expiry(minutes: int) -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=minutes)

def create_access_token(user_id: int, is_admin: bool) -> str:
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": _expiry(_cfg.jwt_access_minutes),
    }
    return jwt.encode(payload, _cfg.jwt_secret, algorithm=_cfg.jwt_algorithm)

def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, _cfg.jwt_secret, algorithms=[_cfg.jwt_algorithm])
    except jwt.PyJWTError:
        return None

def create_refresh_token() -> str:
    return str(uuid.uuid4())
