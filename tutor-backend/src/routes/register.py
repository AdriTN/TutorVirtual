from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from ..database.database import get_connection
from ..auth.security import hash_password

router = APIRouter()

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str
    confirmPassword: str

@router.post("/register", status_code=201)
def register(body: RegisterUser):
    # Verificamos si las contraseñas coinciden
    if body.password != body.confirmPassword:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    # Verificamos si el usuario ya existe con username
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (body.username,))
    user = cursor.fetchone()
    
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Comprobamos si el email ya está en uso
    cursor.execute("SELECT * FROM users WHERE email = %s", (body.email,))
    user = cursor.fetchone()
    
    if user:
        raise HTTPException(status_code=400, detail="El email ya está en uso")
    
    # Encriptamos la contraseña
    hashed_password = hash_password(body.password)
    
    # Creamos el usuario
    cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (body.username, body.email, hashed_password))
    connection.commit()
    
    return {"message": "Usuario creado con éxito"}
    