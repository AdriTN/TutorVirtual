from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...core.security import hash_password
from app.api.schemas.auth import RegisterIn, RegisterOut
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=RegisterOut,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    body: RegisterIn,
    db: Session = Depends(get_db),
) -> RegisterOut:
    """
    Alta de usuario *self-service*.

    1. Comprueba duplicados (username, e-mail).
    2. Hashea contraseña con `bcrypt`.
    3. Devuelve DTO sin exponer el hash.
    """

    dup = (
        db.query(User)
        .filter((User.username == body.username) | (User.email == body.email))
        .first()
    )
    if dup:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese nombre o e-mail",
        )

    new_user = User(
        username=body.username,
        email=body.email,
        password=hash_password(body.password),
    )
    db.add(new_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Usuario duplicado",
        ) from None

    db.refresh(new_user)

    return RegisterOut.model_validate(
        {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
        }
    )
