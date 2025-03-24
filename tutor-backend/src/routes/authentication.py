import datetime
from auth.security import create_refresh_token
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..database.database import get_connection
from ..auth.security import verify_password, create_jwt_token


router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest):
    email = data.email
    password = data.password
    
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password, is_admin FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_id, username, user_email, hashed_password, user_is_admin = user
        if not verify_password(password, hashed_password):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
        token = create_jwt_token({"user_id": user_id, "is_admin": user_is_admin})
        refresh_token = create_refresh_token()
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
        
        cursor.execute(
            "INSERT INTO refresh_tokens (user_id, token, expires_at) VALUES (%s, %s, %s)",
            (user_id, refresh_token, expires_at)
        )
        conn.commit()
        
        return {"message": "Login exitoso", "user_id": user_id, "username": username, "user_email": user_email, "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshRequest):
    old_token = refresh_data.refresh_token
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, user_id, expires_at FROM refresh_tokens WHERE token = %s", (old_token,))
        token = cursor.fetchone()
        if not token:
            raise HTTPException(status_code=404, detail="Token no encontrado")
        
        token_id, user_id, expires_at = token
        if datetime.now(datetime.timezone.utc) > expires_at:
            cursor.execute("DELETE FROM refresh_tokens WHERE id = %s", (token_id,))
            conn.commit()
            raise HTTPException(status_code=400, detail="Token expirado")
        
        new_token = create_refresh_token()
        new_expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        cursor.execute(
            "UPDATE refresh_tokens SET token = %s, expires_at = %s WHERE id = %s",
            (new_token, new_expires_at, token_id)
        )
        conn.commit()
        
        new_access_token = create_jwt_token({"user_id": user_id})
        
        return {"access_token": new_access_token, "refresh_token": new_token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
