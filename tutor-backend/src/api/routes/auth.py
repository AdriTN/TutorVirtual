from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import string

from src.core.config import get_settings

from src.api.schemas.auth import GoogleCode, RegisterIn, RegisterOut
from src.models.user import UserProvider
from sqlalchemy.exc import IntegrityError

from src.api.schemas.authlog import LoginIn, RefreshIn, TokenOut
from src.api.schemas.authlogout import LogoutIn
from src.api.dependencies.auth import jwt_required
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
    google_token_url = "https://oauth2.googleapis.com/token"
    request_data = {
        "code": payload.code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    # Eliminados prints de depuración. Considerar usar logging.
    # print(f"Backend: Intentando intercambiar código con Google. URL: {google_token_url}, Data: {request_data}")

    try:
        token_resp = requests.post(
            google_token_url,
            data=request_data,
            timeout=10, 
        )
    except requests.exceptions.RequestException as req_err:
        # print(f"Backend: Error de conexión al intentar contactar a Google: {req_err}") # Eliminado
        # Considerar loggear req_err para información detallada en el servidor
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error de conexión al servicio de Google.") # Mensaje más genérico para el cliente

    # print(f"Backend: Respuesta de Google. Status: {token_resp.status_code}, Body: {token_resp.text}") # Eliminado
    
    if token_resp.status_code != 200:
        error_detail = {"message": "Error al intercambiar código con Google.", "google_response_status": token_resp.status_code}
        try:
            google_error_payload = token_resp.json()
            error_detail["google_error"] = google_error_payload.get("error")
            error_detail["google_error_description"] = google_error_payload.get("error_description")
        except ValueError:
            error_detail["google_response_text"] = token_resp.text # Incluir texto si no es JSON
        
        # print(f"Backend: Error de Google. Detalle: {error_detail}") # Eliminado
        # Considerar loggear error_detail
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    tokens = token_resp.json()
    # print(f"Backend: Tokens recibidos de Google: {tokens}") # Eliminado

    # 2. Verificar id_token y extraer identidad
    id_token_to_verify = tokens.get("id_token")
    if not id_token_to_verify:
        # print("Backend: Error - No se encontró 'id_token' en la respuesta de Google.") # Eliminado
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 
                            detail="Respuesta de Google no incluyó 'id_token'.")
    
    try:
        # print(f"Backend: Verificando id_token (primeros 20 chars): {id_token_to_verify[:20]}...") # Eliminado
        idinfo = google_id_token.verify_oauth2_token(
            id_token_to_verify,
            google_requests.Request(),
            settings.google_client_id, 
            clock_skew_in_seconds=5 # Aumentado ligeramente el margen de reloj
        )
        # print(f"Backend: id_token verificado. Email: {idinfo.get('email')}") # Eliminado
    except ValueError as e:
        # print(f"Backend: Error al verificar id_token: {e}") # Eliminado
        # Considerar loggear e
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"id_token inválido o no verificado.") # Mensaje más genérico

    sub = idinfo.get("sub")
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


@router.post("/logout",
             status_code=status.HTTP_204_NO_CONTENT,
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
) -> None:
    """
    Elimina de la base de datos el *refresh token* indicado.
    """
    token_row = (
        db.query(RefreshToken)
        .filter_by(token=payload.refresh_token, user_id=user["user_id"])
        .one_or_none()
    )
    if token_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado",
        )

    db.delete(token_row)
    db.commit()


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

    return RegisterOut.model_validate(
        {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    )
