from fastapi import APIRouter, HTTPException
from ..database.database import get_connection

router = APIRouter()

@router.get("/users")
def create_user(name: str, email: str, password: str):
    connection = get_connection()
    cursor = connection.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO users (username, email, password)
            VALUES (%s, %s, %s)
        """, (name, email, password))
        
        user_id = cursor.fetchone()[0]
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
    
    return {"id": user_id, "username": name, "email": email}