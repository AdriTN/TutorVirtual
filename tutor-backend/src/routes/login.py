from fastapi import APIRouter, HTTPException, status
from ..database.database import get_connection
from ..auth.auth import hash_password, verify_password, create_jwt_token


router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_id, username, user_email, hashed_password, user_is_admin = user
        if not verify_password(password, hashed_password):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
        token = create_jwt_token({"user_id": user_id, "is_admin": user_is_admin})
        return {"message": "Login exitoso", "user_id": user_id, "username": username, "user_email": user_email, "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
