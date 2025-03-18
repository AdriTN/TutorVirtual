from fastapi import APIRouter, HTTPException, status
from src.database.database import get_connection
from src.auth.auth import hash_password, verify_password, create_jwt_token

router = APIRouter()

@router.post("/login/")
def login(email: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")
            
            user_id, hashed_password = user[0], user[1]
            
            if not verify_password(password, hashed_password):
                raise HTTPException(status_code=400, detail="Contraseña incorrecta")
            
            token = create_jwt_token({"id": user_id, "email": email})
            return {"token": token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
