from datetime import datetime, timedelta, timezone
import random
import string

from src.core.config import get_settings

from src.api.schemas.auth import GoogleCode
from src.api.schemas.google import GoogleToken
from src.models.user import UserProvider
from sqlalchemy.exc import IntegrityError

from src.api.schemas.authlog import LoginIn, RefreshIn, TokenOut
from fastapi import APIRouter, Depends, HTTPException, status
import requests
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from sqlalchemy  import delete
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from src.models import User, RefreshToken
from src.core.security import hash_password

router = APIRouter()

settings = get_settings()


# ──────────── Endpoints ───────────
@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user: User | None = (
        db.query(User).filter(User.email == data.email.lower()).first()
    )
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Credenciales inválidas")

    access_token = create_access_token(user.id, user.is_admin)
    refresh_token = _store_refresh(user, db)

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
def refresh(data: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    stored: RefreshToken | None = (
        db.query(RefreshToken).filter_by(token=data.refresh_token).first()
    )
    if not stored:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido")

    # ── token caducado ────────────────────────────────────────────────────
    exp = stored.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp < datetime.now(timezone.utc):
        db.execute(delete(RefreshToken).where(RefreshToken.id == stored.id))
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token expirado")

    # ── rotación garantizando unicidad ───────────────────────────────────
    while True:
        stored.token = create_refresh_token()
        stored.expires_at = datetime.now(timezone.utc) + timedelta(days=3)
        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()

    user: User = db.get(User, stored.user_id)

    return TokenOut(
        access_token=create_access_token(user.id, user.is_admin),
        refresh_token=stored.token,
    )

@router.post("/google", response_model=TokenOut)
def google_login(payload: GoogleCode, db: Session = Depends(get_db)) -> TokenOut:
    # 1. Intercambiar el code por tokens de Google
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": payload.code,
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri": "postmessage",
            "grant_type": "authorization_code",
        },
        timeout=5,
    )
    
    if token_resp.status_code != 200:
        raise HTTPException(status.HTTP_400_BAD_REQUEST,
                            f"Google token error: {token_resp.text}")

    tokens = token_resp.json()

    # 2. Verificar id_token y extraer identidad
    try:
        idinfo = google_id_token.verify_oauth2_token(
            tokens["id_token"],
            google_requests.Request(),
            settings.google_client_id,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"id_token inválido: {e}")

    sub   = idinfo["sub"]
    email = idinfo["email"]

    # 3. Buscar o crear usuario local
    provider = (db.query(UserProvider)
                  .filter_by(provider="google", provider_user_id=sub)
                  .first())

    if provider:
        user = db.get(User, provider.user_id)
    else:
        username = email.split("@")[0]
        # evita colisiones de usernames
        base, i = username, 1
        while db.query(User).filter_by(username=username).first():
            username = f"{base}{i}"; i += 1

        user = User(username=username,
                    email=email,
                    password=hash_password(generate_password()))
        db.add(user); db.commit(); db.refresh(user)

        db.add(UserProvider(user_id=user.id,
                            provider="google",
                            provider_user_id=sub))
        db.commit()

    # 4. Emitir tokens
    access  = create_access_token(user.id, user.is_admin)
    refresh = create_refresh_token()
    db.add(RefreshToken(user_id=user.id,
                        token=refresh,
                        expires_at=datetime.now(timezone.utc)+timedelta(days=3)))
    db.commit()

    return TokenOut(access_token=access, refresh_token=refresh)


# ──────────── helpers ────────────
def _expiry(*, days: int = 0, minutes: int = 0):
    return datetime.now(timezone.utc) + timedelta(days=days, minutes=minutes)


def _store_refresh(user: User, db: Session) -> str:
    token = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token=token,
            expires_at=_expiry(days=3),
        )
    )
    db.commit()
    return token

def generate_password(longitud=12):
    """
    Genera una contraseña aleatoria de la longitud especificada (por defecto 12).
    Se asegura de que cumpla con los requisitos:
      - Al menos 1 minúscula
      - Al menos 1 mayúscula
      - Al menos 1 dígito
      - Al menos 1 carácter especial
      - Longitud mínima de 8
    """
    if longitud < 8:
        raise ValueError("La longitud mínima de la contraseña debe ser 8.")

    # Categorías de caracteres
    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    especiales = string.punctuation

    # Forzar al menos un carácter de cada tipo
    password = [
        random.choice(minusculas),
        random.choice(mayusculas),
        random.choice(digitos),
        random.choice(especiales),
    ]

    # Rellenar el resto con cualquier carácter
    todos = minusculas + mayusculas + digitos + especiales
    for _ in range(longitud - 4):
        password.append(random.choice(todos))

    # Mezclar para no dejar patrones predecibles
    random.shuffle(password)

    return "".join(password)
