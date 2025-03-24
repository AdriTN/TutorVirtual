import datetime
import os
import random
import string
import requests


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database.database import get_connection
from ..auth.security import create_jwt_token, create_refresh_token, hash_password
from dotenv import load_dotenv


router = APIRouter()

load_dotenv()

class GoogleToken(BaseModel):
    token: str
    

@router.post("/google")
def google_login(token: GoogleToken):
    # LLamada a la api de google para validar el access token y obtener la informacion del usuario
    try:
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={"access_token": token.token}
        )
        print("Respuesta de Google:", userinfo_response.json())
    except Exception as e:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    user_info = userinfo_response.json()
    user_google_id = user_info.get("sub")
    email = user_info.get("email")
    
    if not user_google_id or not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener la información del usuario")
    
    connection = get_connection()
    cursor = connection.cursor()
    
    # Buscar en la tabla de proveedores si ya existe un registro para este usuario de Google
    cursor.execute("""
        SELECT user_id 
        FROM users_providers 
        WHERE provider_user_id = %s AND provider = %s
    """, (user_google_id, "google"))
    result = cursor.fetchone()
    
    if result:
        # El usuario ya existe → realizar login
        user_id = result[0]
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        user_id, username, user_email, is_admin = user
        
        jwt_token = create_jwt_token({"user_id": user_id, "is_admin": is_admin})
        refresh_token = create_refresh_token()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        
        cursor.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user_id, refresh_token, expires_at)
        )
        connection.commit()
        cursor.close()
        connection.close()
    
    # Si no existe, registramos al usuario
    username = email.split("@")[0]
    # Verificar si el username ya existe y modificarlo si es necesario
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        i = 1
        base_username = username
        while existing_user:
            username = f"{base_username}{i}"
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()
            i += 1
    
    # Crear una contraseña aleatoria (el usuario no la usará, ya que se autenticará con Google)
    password = generar_password()
    hashed_password = hash_password(password)
    
    # Insertar el nuevo usuario y obtener su ID
    cursor.execute("""
        INSERT INTO users (username, email, password) 
        VALUES (%s, %s, %s) 
        RETURNING id
    """, (username, email, hashed_password))
    new_user_id = cursor.fetchone()[0]
    
    # Registrar la relación en la tabla de proveedores
    cursor.execute("""
        INSERT INTO users_providers (user_id, provider, provider_user_id) 
        VALUES (%s, %s, %s)
    """, (new_user_id, "google", user_google_id))
    
    # Generar tokens para el nuevo usuario
    jwt_token = create_jwt_token({"user_id": new_user_id, "is_admin": False})
    refresh_token = create_refresh_token()
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    cursor.execute(
        "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
        (new_user_id, refresh_token, expires_at)
    )
    connection.commit()
    cursor.close()
    connection.close()


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
