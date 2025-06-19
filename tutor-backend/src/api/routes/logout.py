from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.models import RefreshToken
from src.api.schemas.authlogout import LogoutIn

router = APIRouter()


@router.post("/logout",
             status_code=status.HTTP_204_NO_CONTENT,
             summary="Invalidate a refresh token",
             responses={
                 204: {"description": "Token invalidado correctamente"},
                 404: {"description": "Token no encontrado"},
             })
def logout(
    payload: LogoutIn,
    user: dict = Depends(jwt_required),
    *,
    db: Session = Depends(get_db),
) -> None:
    """
    Elimina de la base de datos el *refresh token* indicado.
    """
    token_row = (
        db.query(RefreshToken)
        .filter_by(token=payload.refresh_token, user_id=user["user_id"])
        .one_or_none()
    )
    if token_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token no encontrado",
        )

    db.delete(token_row)
    db.commit()
