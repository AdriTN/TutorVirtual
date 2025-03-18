from fastapi import APIRouter, HTTPException
from ..database.database import get_connection

router = APIRouter()

@router.post("/users/", status_code=201)
def create_user(name: str, email: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id", (name, email, password))
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        return {"id": user_id, "name": name, "email": email, "password": password}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/users/")
def get_users():
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    users = []
    for row in rows:
        users.append({"id": row[0], "name": row[1], "email": row[2], "password": row[3]})
    return users