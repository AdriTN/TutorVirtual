from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import string

import structlog

from src.core.config import get_settings

from src.api.schemas.auth import GoogleCode, RegisterIn, RegisterOut
from src.models.user import UserProvider
from sqlalchemy.exc import IntegrityError

from src.api.schemas.authlog import LoginIn, RefreshIn, TokenOut
from src.api.schemas.authlogout import LogoutIn
from src.api.dependencies.auth import jwt_required
from fastapi import APIRouter, Depends, HTTPException, status, Response
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
logger = structlog.get_logger(__name__)
settings = get_settings()


# ──────────── Endpoints ───────────
@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user: User | None = (
        db.query(User).filter(User.email == data.email.lower()).first()
    )
    if not user or not verify_password(data.password, user.password):
        logger.warn("Intento de login fallido", email=data.email.lower())
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Credenciales inválidas")

    access_token = create_access_token(user.id, user.is_admin)
    refresh_token = _store_refresh(user, db)
    logger.info("Usuario ha iniciado sesión", user_id=user.id, email=user.email)

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
def refresh(data: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    stored: RefreshToken | None = (
        db.query(RefreshToken).filter_by(token=data.refresh_token).first()
    )
    if not stored:
        logger.error("Intento de refrescar token inválido", refresh_token=data.refresh_token)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido")

    exp = stored.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)

    if exp < datetime.now(timezone.utc):
        logger.error("Intento de refrescar token expirado", refresh_token=data.refresh_token, user_id=stored.user_id, expired_at=exp.isoformat())
        db.execute(delete(RefreshToken).where(RefreshToken.id == stored.id))
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token expirado")

    while True:
        stored.token = create_refresh_token()
        stored.expires_at = datetime.now(timezone.utc) + timedelta(days=3)
        try:
            db.commit()
            break
        except IntegrityError:
            db.rollback()

    user: User = db.get(User, stored.user_id)
    logger.info("Token refrescado", user_id=user.id)

    return TokenOut(
        access_token=create_access_token(user.id, user.is_admin),
        refresh_token=stored.token,
    )

@router.post("/google", response_model=TokenOut)
def google_login(payload: GoogleCode, db: Session = Depends(get_db)) -> TokenOut:
    # 1. Intercambiar el code por tokens de Google
    google_token_url = "https://oauth2.googleapis.com/token"
    request_data = {
        "code": payload.code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    logger.info("Intentando intercambiar código con Google", url=google_token_url)

    try:
        token_resp = requests.post(
            google_token_url,
            data=request_data,
            timeout=10, 
        )
    except requests.exceptions.RequestException as req_err:
        logger.error("Error de conexión al contactar a Google", exc_info=req_err, url=google_token_url)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error de conexión al servicio de Google.")

    logger.info("Respuesta de Google recibida", status_code=token_resp.status_code, response_text=token_resp.text)
    
    if token_resp.status_code != 200:
        error_detail = {"message": "Error al intercambiar código con Google.", "google_response_status": token_resp.status_code}
        try:
            google_error_payload = token_resp.json()
            error_detail["google_error"] = google_error_payload.get("error")
            error_detail["google_error_description"] = google_error_payload.get("error_description")
        except ValueError:
            error_detail["google_response_text"] = token_resp.text
        
        logger.error("Error de Google al intercambiar código", detail=error_detail)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    tokens = token_resp.json()
    logger.info("Tokens recibidos de Google", token_keys=list(tokens.keys())) # No loguear tokens directamente por seguridad

    # 2. Verificar id_token y extraer identidad
    id_token_to_verify = tokens.get("id_token")
    if not id_token_to_verify:
        logger.error("No se encontró 'id_token' en la respuesta de Google", google_response_keys=list(tokens.keys()))
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 
                            detail="Respuesta de Google no incluyó 'id_token'.")
    
    logger.info("Verificando id_token")
    try:
        idinfo = google_id_token.verify_oauth2_token(
            id_token_to_verify,
            google_requests.Request(),
            settings.google_client_id, 
            clock_skew_in_seconds=5 
        )
        logger.info("id_token verificado", email=idinfo.get('email'), google_user_id=idinfo.get('sub'))
    except ValueError as e:
        logger.error("Error al verificar id_token", exc_info=e)
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"id_token inválido o no verificado.")

    sub = idinfo.get("sub")
    email = idinfo["email"]

    # 3. Buscar o crear usuario local
    provider = (db.query(UserProvider)
                  .filter_by(provider="google", provider_user_id=sub)
                  .first())

    if provider:
        user = db.get(User, provider.user_id)
        logger.info("Usuario existente ha iniciado sesión con Google", user_id=user.id, email=user.email, google_user_id=sub)
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
        logger.info("Nuevo usuario registrado con Google", user_id=user.id, email=user.email, username=user.username, google_user_id=sub)

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

    minusculas = string.ascii_lowercase
    mayusculas = string.ascii_uppercase
    digitos = string.digits
    especiales = string.punctuation

    password = [
        random.choice(minusculas),
        random.choice(mayusculas),
        random.choice(digitos),
        random.choice(especiales),
    ]

    todos = minusculas + mayusculas + digitos + especiales
    for _ in range(longitud - 4):
        password.append(random.choice(todos))

    random.shuffle(password)

    return "".join(password)


@router.post("/logout",
             summary="Invalidate a refresh token",
             responses={
                 204: {"description": "Token invalidado correctamente"},
                 404: {"description": "Token no encontrado"},
             })
def logout(
    payload: LogoutIn,
    user: dict = Depends(jwt_required),
    *,
    db: Session = Depends(get_db),
) -> Response:
    """
    Elimina de la base de datos el *refresh token* indicado.
    """
    logger.info("Intento de logout", user_id=user["user_id"], refresh_token_prefix=payload.refresh_token[:8] + "...")
    token_row = (
        db.query(RefreshToken)
        .filter_by(token=payload.refresh_token, user_id=user["user_id"])
        .one_or_none()
    )
    if token_row is None:
        logger.warn("Token de refresco no encontrado durante logout", user_id=user["user_id"], refresh_token_prefix=payload.refresh_token[:8] + "...")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado",
        )

    db.delete(token_row)
    db.commit()
    logger.info("Logout exitoso, token invalidado", user_id=user["user_id"], refresh_token_id=token_row.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/register",
    response_model=RegisterOut,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    body: RegisterIn,
    db: Session = Depends(get_db),
) -> RegisterOut:
    """
    Alta de usuario *self-service*.

    1. Comprueba duplicados (username, e-mail).
    2. Hashea contraseña con `bcrypt`.
    3. Devuelve DTO sin exponer el hash.
    """
    logger.info("Intento de registro de nuevo usuario", username=body.username, email=body.email)

    dup = (
        db.query(User)
        .filter((User.username == body.username) | (User.email == body.email))
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese nombre o e-mail",
        )

    new_user = User(
        username=body.username,
        email=body.email,
        password=hash_password(body.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuario duplicado",
        ) from None

    db.refresh(new_user)
    logger.info("Usuario registrado exitosamente", user_id=new_user.id, username=new_user.username, email=new_user.email)

    return RegisterOut.model_validate(
        {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    )
