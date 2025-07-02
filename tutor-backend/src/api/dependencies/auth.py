from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.core.security import decode_token
from src.database.session import get_db
from src.models.user import User
from sqlalchemy.orm import Session
import logging


security = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def jwt_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing token")

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return payload

def admin_required(payload: dict = Depends(jwt_required)):
    if not payload.get("is_admin"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin privileges required")
    return payload

def get_current_user(
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia de FastAPI para obtener el objeto User autenticado actual.

    Usa jwt_required para asegurar que el token es válido y obtener su payload.
    Luego, usa el user_id del payload para cargar el objeto User desde la BD.
    """
    user_id = payload.get("user_id")

    if user_id is None:
        logger.warn("get_current_user: user_id no encontrado en el payload del token.", token_payload=payload)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID no encontrado en el token. Token inválido o malformado.",
        )

    user = db.get(User, user_id)

    if user is None:
        logger.error("get_current_user: Usuario no encontrado en la BD para user_id en token válido.", user_id_from_token=user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado. Por favor, inicie sesión de nuevo.",
        )
    
    logger.debug("get_current_user: Usuario recuperado.", user_id=user.id, username=user.username)
    return user
