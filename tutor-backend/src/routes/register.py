from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..dependencies.database_dependencies import get_db
from ..dependencies.security import hash_password
from ..models.user import User

router = APIRouter()

class RegisterUser(BaseModel):
    username: str
    email: str
    password: str
    confirmPassword: str

@router.post("/register", status_code=201)
def register(body: RegisterUser, db: Session = Depends(get_db)):
    if body.password != body.confirmPassword:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden")
    
    user = db.query(User).filter( (User.username == body.username) | (User.email == body.email) ).first()
    
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    hashed_password = hash_password(body.password)
    
    new_user = User(
        username=body.username,
        email=body.email,
        password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "Usuario creado exitosamente",
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email
    }
    