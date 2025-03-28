from fastapi import APIRouter, HTTPException, Depends
from ..dependencies.database_dependencies import get_db
from ..dependencies.security import hash_password
from ..dependencies.auth_dependencies import admin_required, jwt_required
from pydantic import BaseModel
from ..models.user import User
from sqlalchemy.orm import Session

router = APIRouter()

# Endpoints para usuarios

@router.get("/users/me")
def get_my_data(playload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user_id = playload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return {
        "id": user.id,
        "name": user.username,
        "email": user.email,
    }

@router.delete("/users/{id}")
def delete_user(id: int, dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Usuario eliminado"}


# Endpoints para administradores

@router.post("/users/{user_id}/promote")
def promote_to_admin(user_id: int, playload: dict = Depends(admin_required), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_admin = True
    db.commit()
    
    return {"message": f"Usuario {user_id} promovido a administrador"}

@router.get("/users")
def get_users(playload: dict = Depends(admin_required), db: Session = Depends(get_db)):
    users = db.query(User).all()
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
        })
    
    return result
