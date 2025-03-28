from dependencies.auth_dependencies import jwt_required
from dependencies.database_dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..models.user import RefreshToken


router = APIRouter()

class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/logout")
def logout(logout_data: LogoutRequest, playload: dict = Depends(jwt_required), db: get_db = Depends()):
    token_to_delete = logout_data.refresh_token
    
    refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token_to_delete).first()
    
    if not refresh_token:
        raise HTTPException(status_code=404, detail="Token no encontrado")
    
    db.delete(refresh_token)
    db.commit()
    
    return {"message": "Sesión cerrada"}