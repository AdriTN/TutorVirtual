from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...api.dependencies.auth import jwt_required
from ...models import RefreshToken

router = APIRouter(prefix="/auth", tags=["Auth"])


class LogoutIn(BaseModel):
    refresh_token: str


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: LogoutIn, _: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    row = db.query(RefreshToken).filter(RefreshToken.token == data.refresh_token).first()
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Token no encontrado")
    db.delete(row)
    db.commit()
