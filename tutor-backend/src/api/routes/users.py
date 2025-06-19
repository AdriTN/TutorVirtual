from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models import User

router = APIRouter()


@router.get("/me")
def me(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user: User | None = db.query(User).get(payload["user_id"])
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return {"id": user.id, "username": user.username, "email": user.email}


@router.get("/all", dependencies=[Depends(admin_required)])
def list_users(db: Session = Depends(get_db)):
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.is_admin,
        }
        for u in db.query(User).all()
    ]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, _: dict = Depends(admin_required), db: Session = Depends(get_db)
):
    user: User | None = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    db.delete(user)
    db.commit()


@router.post("/{user_id}/promote")
def promote(
    user_id: int, _: dict = Depends(admin_required), db: Session = Depends(get_db)
):
    user: User | None = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    user.is_admin = True
    db.commit()
    return {"detail": "Promocionado a admin"}
