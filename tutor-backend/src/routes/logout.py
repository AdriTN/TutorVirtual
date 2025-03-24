from auth.auth_dependencies import jwt_required
from database.database import get_connection
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel


router = APIRouter()

class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/logout")
def logout(logout_data: LogoutRequest, playload: dict = Depends(jwt_required)):
    token_to_delete = logout_data.refresh_token
    conn = get_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="No hay conexión a la BD")
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM refresh_tokens WHERE token = %s", (token_to_delete,))
        conn.commit()
        return {"message": "Logout exitoso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
