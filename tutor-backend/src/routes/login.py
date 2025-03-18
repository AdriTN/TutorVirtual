from fastapi import APIRouter, HTTPException, status
from src.database.database import get_connection
from src.auth.auth import hash_password, verify_password, create_jwt_token

router = APIRouter()

@router.post("/login")
def login(email: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, password FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        user_id, name, email, hashed_password = user
        if not verify_password(password, hashed_password):
            raise HTTPException(status_code=400, detail="Contraseña incorrecta")
        
        token = create_jwt_token(user_id)
        return {"message": "Login exitoso", "user_id": user_id, "token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
