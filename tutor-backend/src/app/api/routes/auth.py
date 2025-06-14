from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
)
from ...models import User, RefreshToken

router = APIRouter(prefix="/auth", tags=["Auth"])


# ──────────── Pydantic ────────────
class LoginIn(BaseModel):
    email: EmailStr
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str


# ──────────── Endpoints ───────────
@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)) -> TokenOut:
    user: User | None = (
        db.query(User).filter(User.email == data.email.lower()).first()
    )
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Credenciales inválidas")

    access_token = create_access_token(user.id, user.is_admin)
    refresh_token = _store_refresh(user, db)

    return TokenOut(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenOut)
def refresh(data: RefreshIn, db: Session = Depends(get_db)) -> TokenOut:
    stored: RefreshToken | None = (
        db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    )
    if not stored:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token inválido")

    if stored.expires_at < datetime.now(timezone.utc):
        db.delete(stored)
        db.commit()
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token expirado")

    # rotación
    stored.token = create_refresh_token()
    stored.expires_at = _expiry(days=3)
    db.commit()
    db.refresh(stored)

    user: User = db.query(User).get(stored.user_id)

    return TokenOut(
        access_token=create_access_token(user.id, user.is_admin),
        refresh_token=stored.token,
    )


# ──────────── helpers ────────────
def _expiry(*, days: int = 0, minutes: int = 0):
    return datetime.now(timezone.utc) + timedelta(days=days, minutes=minutes)


def _store_refresh(user: User, db: Session) -> str:
    token = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token=token,
            expires_at=_expiry(days=3),
        )
    )
    db.commit()
    return token
