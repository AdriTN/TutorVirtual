import datetime
import os
import random
import string
import requests


from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..dependencies.database_dependencies import get_db
from ..dependencies.security import create_jwt_token, create_refresh_token, hash_password
from dotenv import load_dotenv
from models.user import User, UserProvider, RefreshToken


router = APIRouter()

load_dotenv()

class GoogleToken(BaseModel):
    token: str
    

@router.post("/google")
def google_login(token: GoogleToken, db: Session = Depends(get_db)):
    try:
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={"access_token": token.token}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    user_info = userinfo_response.json()
    user_google_id = user_info.get("sub")
    email = user_info.get("email")
    
    if not user_google_id or not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener la información del usuario")
    
    user_provider = db.query(UserProvider).filter(UserProvider.provider_user_id == user_google_id, UserProvider.provider == "google").first()
    
    if user_provider:
        user = db.query(User).filter(User.id == user_provider.user_id).first()
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        
        jwt_token = create_jwt_token({"user_id": user.id, "is_admin": user.is_admin})
        refresh_token = create_refresh_token()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        
        new_refresh_token = RefreshToken(user_id=user.id, token=refresh_token, expires_at=expires_at)
        db.add(new_refresh_token)
        db.commit()
        db.refresh(new_refresh_token)
        
        return {
            "message": "Login exitoso",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "access_token": jwt_token,
            "refresh_token": refresh_token
        }
    
    username = email.split("@")[0]
    
    existing_user = db.query(User).filter(User.username == username).first()
    
    if existing_user:
        i = 1
        base_username = username
        while existing_user:
            username = f"{base_username}{i}"
            existing_user = db.query(User).filter(User.username == username).first()
            i += 1
    

    password = generar_password()
    hashed_password = hash_password(password)
    
    new_user = User(username=username, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    

    new_provider = UserProvider(user_id=new_user.id, provider="google", provider_user_id=user_google_id)
    db.add(new_provider)
    db.commit()
    db.refresh(new_provider)
    
    
    jwt_token = create_jwt_token({"user_id": new_user.id, "is_admin": new_user.is_admin})
    refresh_token = create_refresh_token()
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    
    new_refresh_token = RefreshToken(user_id=new_user.id, token=refresh_token, expires_at=expires_at)
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    
    return {
        "message": "Usuario registrado",
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "access_token": jwt_token,
        "refresh_token": refresh_token
    }


def generar_password(longitud=12):
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
