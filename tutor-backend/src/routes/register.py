from fastapi import APIRouter, HTTPException, status
from src.database import get_connection
from src.auth.auth import hash_password, verify_password, create_jwt_token

router = APIRouter()

@router.post("/register/", status_code=201)
def register(name: str, email: str, password: str):
    hashed_password = hash_password(password)
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (name, email, hashed_password))
            user_id = cursor.fetchone()[0]
            conn.commit()
        return {"id": user_id, "name": name, "email": email}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
