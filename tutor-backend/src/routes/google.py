import os
import random
import string
import requests


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database.database import get_connection
from ..auth.auth import hash_password
from dotenv import load_dotenv


router = APIRouter()

load_dotenv()

class GoogleToken(BaseModel):
    token: str
    
@router.post("/register/google")
def google_login(token: GoogleToken):
    # LLamada a la api de google para validar el access token y obtener la informacion del usuario
    try:
        userinfo_response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            params={"access_token": token.token}
        )
        print(userinfo_response.json())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user_info = userinfo_response.json()
    user_google_id = user_info.get("sub")
    email = user_info.get("email")
    
    if not user_google_id or not email:
        raise HTTPException(status_code=400, detail="No se pudo obtener la informacion del usuario")
    
    # Revisamos si el usuario ya existe en la base de datos
    # Si existe, hacemos login. Si no, lo registramos
    connection = get_connection()
    cursor = connection.cursor()
    
    # Buscamos el usuario en la tabla de usuarios_providers
    cursor.execute("""
                   SELECT user_id 
                   FROM users_providers 
                   WHERE provider_user_id = %s 
                   AND provider = %s
                   """, ("google", user_google_id,))
    user = cursor.fetchone()
    
    if user:
        # El usuario ya existe, hacemos login
        cursor.execute("SELECT id, username, email, is_admin FROM users WHERE id = %s", (user[0],))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(status_code=400, detail="Usuario no encontrado")
        
        cursor.close()
        connection.close()
        
        return {
            "Login con Google sin implementar"
        }
    
    # El usuario no existe, lo registramos
    username = email.split("@")[0]
    
    # Compobamos si el username ya existe y generamos un nuevo nombre de forma iterativa hasta encontrar uno disponible
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    
    if user:
        i = 1
        while user:
            username = f"{username}{i}"
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            i += 1
    
    # Creamos una contraseña aleatoria que cumpla con las restricciones y la encriptamos
    password = generar_password()
    hashed_password = hash_password(password)
    
    # Creamos el usuario
    cursor.execute("""INSERT INTO users (username, email, password) 
                   VALUES (%s, %s, %s) 
                   RETURNING id
                   """, (username, email, hashed_password))
    user_id = cursor.fetchone()[0]
    
    # Lo insertamos en la tabla de usuarios_providers
    cursor.execute("""INSERT INTO users_providers (user_id, provider, provider_user_id) 
                   VALUES (%s, %s, %s)
                   """, (user_id, "google", user_google_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return {
        "message": "Usuario creado con éxito"
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
