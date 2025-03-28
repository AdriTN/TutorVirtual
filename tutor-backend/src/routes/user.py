from fastapi import APIRouter, HTTPException, Depends
from ..database.database import get_connection
from ..auth.security import hash_password
from ..auth.auth_dependencies import admin_required, jwt_required
from pydantic import BaseModel

router = APIRouter()

# Endpoints para usuarios
@router.post("/users", status_code=201)
def create_user(name: str, email: str, password: str):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        hased_password = hash_password(password)
        
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO users (username, email, password) 
                       VALUES (%s, %s, %s) 
                       RETURNING id
                       """, (name, email, hased_password))
        user_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        
        return {"id": user_id, "name": name, "email": email}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
        

@router.get("/users/me")
def get_my_data(playload: dict = Depends(jwt_required)):
    user_id = playload.get("user_id")
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {"id": user[0], "name": user[1], "email": user[2]}

@router.delete("/users/{id}")
def delete_user(id: int, dict = Depends(jwt_required)):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        return {"message": "Usuario eliminado"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()


# Endpoints para administradores

@router.post("/users/{user_id}/promote")
def promote_to_admin(user_id: int, playload: dict = Depends(admin_required)):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_admin = true WHERE id = %s", (user_id,))
        conn.commit()
        cursor.close()
        return {"message": f"Usuario {user_id} ahora es admin"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@router.get("/users")
def get_users(playload: dict = Depends(admin_required)):
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password, is_admin FROM users")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    users = []
    for row in rows:
        users.append({"id": row[0], "name": row[1], "email": row[2], "password": row[3]})
    return users
