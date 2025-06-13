import uuid
import bcrypt
import jwt
import os
import datetime
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

def _expiry(minutes: int = 30) -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(minutes=minutes)

def create_jwt_token(user_id: int, is_admin: bool, minutes=30) -> str:
    payload = {
        "user_id": user_id,
        "is_admin": is_admin,
        "exp": _expiry(minutes)
        }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return token

def decode_jwt_token(token: str) -> dict:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def create_refresh_token() -> str:
    return str(uuid.uuid4())

def strip_and_lower(s: str) -> str:
    return s.strip().lower()

