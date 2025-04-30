import datetime
from dependencies.security import create_refresh_token
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from ..dependencies.database_dependencies import get_db
from ..dependencies.security import verify_password, create_jwt_token
from sqlalchemy.orm import Session
from models.user import User, RefreshToken


router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email
    password = data.password
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    if not verify_password(password, user.password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")
    
    access_token = create_jwt_token({"user_id": user.id, "is_admin": user.is_admin})
    refresh_token = create_refresh_token()
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
    
    new_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=expires_at
    )
    db.add(new_refresh_token)
    db.commit()
    db.refresh(new_refresh_token)
    
    return {
        "message": "Login exitoso",
        "user_id": user.id,
        "username": user.username,
        "user_email": user.email,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshRequest, db: Session = Depends(get_db)):
    old_token = refresh_data.refresh_token
    refresh_db = db.query(RefreshToken).filter(RefreshToken.token == old_token).first()
    
    if not refresh_db:
        raise HTTPException(status_code=400, detail="Token inválido")
    
    if refresh_db.expires_at < datetime.datetime.now(datetime.timezone.utc):
        db.delete(refresh_db)
        db.commit()
        raise HTTPException(status_code=400, detail="Token expirado")
    
    new_refresh_token = create_refresh_token()
    new_expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=3)
    
    refresh_db.token = new_refresh_token
    refresh_db.expires_at = new_expires_at
    db.commit()
    db.refresh(refresh_db)
    
    user = db.query(User).filter(User.id == refresh_db.user_id).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no encontrado")
    
    new_access_token = create_jwt_token({"user_id": user.id, "is_admin": user.is_admin})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token
    }
