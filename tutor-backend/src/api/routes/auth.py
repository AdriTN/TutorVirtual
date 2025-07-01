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
    google_token_url = "https://oauth2.googleapis.com/token"
    request_data = {
        "code": payload.code,
        "client_id": settings.google_client_id,
        "client_secret": settings.google_client_secret,
        "redirect_uri": settings.google_redirect_uri,
        "grant_type": "authorization_code",
    }
    
    print(f"Backend: Intentando intercambiar código con Google. URL: {google_token_url}, Data: {request_data}")

    try:
        token_resp = requests.post(
            google_token_url,
            data=request_data,
            timeout=10, # Aumentado timeout por si acaso
        )
    except requests.exceptions.RequestException as req_err:
        print(f"Backend: Error de conexión al intentar contactar a Google: {req_err}")
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                            f"Error de conexión al servicio de Google: {req_err}")

    print(f"Backend: Respuesta de Google. Status: {token_resp.status_code}, Body: {token_resp.text}")
    
    if token_resp.status_code != 200:
        # Devolvemos el error exacto de Google para diagnóstico
        error_detail = {"message": "Error al intercambiar código con Google.", "google_response": token_resp.text}
        try:
            # Intenta parsear el error de Google si es JSON
            error_detail["google_response_json"] = token_resp.json()
        except ValueError:
            pass # No era JSON, se queda con el texto plano
        
        print(f"Backend: Error de Google. Detalle: {error_detail}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_detail)

    tokens = token_resp.json()
    print(f"Backend: Tokens recibidos de Google: {tokens}")

    # 2. Verificar id_token y extraer identidad
    id_token_to_verify = tokens.get("id_token")
    if not id_token_to_verify:
        print("Backend: Error - No se encontró 'id_token' en la respuesta de Google.")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 
                            detail="No se recibió 'id_token' de Google.")
    
    try:
        print(f"Backend: Verificando id_token (primeros 20 chars): {id_token_to_verify[:20]}...")
        idinfo = google_id_token.verify_oauth2_token(
            id_token_to_verify,
            google_requests.Request(),
            settings.google_client_id, # Audiencia esperada
            clock_skew_in_seconds=2   # Aumentar margen de reloj permitido
        )
        print(f"Backend: id_token verificado. Email: {idinfo.get('email')}")
    except ValueError as e:
        print(f"Backend: Error al verificar id_token: {e}")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"id_token inválido o no verificado: {e}")

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
