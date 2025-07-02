import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required, admin_required
from src.models import User

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/me")
def me(payload: dict = Depends(jwt_required), db: Session = Depends(get_db)):
    user_id = payload["user_id"]
    logger.info("Solicitando detalles del usuario (me)", user_id=user_id)
    user: User | None = db.query(User).get(user_id)
    if not user:
        logger.warn("Usuario no encontrado para endpoint /me", user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    logger.info("Detalles del usuario (me) obtenidos", user_id=user.id, username=user.username, email=user.email)
    return {"id": user.id, "username": user.username, "email": user.email, "is_admin": user.is_admin}


@router.get("/all", dependencies=[Depends(admin_required)])
def list_users(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    admin_user_id = payload["user_id"]
    logger.info("Listando todos los usuarios (admin)", admin_user_id=admin_user_id)
    users = db.query(User).all()
    logger.info("Usuarios listados (admin)", count=len(users), admin_user_id=admin_user_id)
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.is_admin,
        }
        for u in users
    ]


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int, payload: dict = Depends(admin_required), db: Session = Depends(get_db)
):
    admin_user_id = payload["user_id"]
    logger.info("Intentando eliminar usuario (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
    user: User | None = db.query(User).get(user_id)
    if not user:
        logger.warn("Usuario no encontrado al intentar eliminar (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario a eliminar no encontrado")
    
    if user_id == admin_user_id:
        logger.error("Intento de auto-eliminación de admin", target_user_id=user_id, admin_user_id=admin_user_id)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Un administrador no se puede eliminar a sí mismo.")

    db.delete(user)
    db.commit()
    logger.info("Usuario eliminado exitosamente (admin)", target_user_id=user_id, admin_user_id=admin_user_id)


@router.post("/{user_id}/promote", response_model=dict)
def promote(
    user_id: int, payload: dict = Depends(admin_required), db: Session = Depends(get_db)
):
    admin_user_id = payload["user_id"]
    logger.info("Intentando promover usuario a admin (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
    user: User | None = db.query(User).get(user_id)
    if not user:
        logger.warn("Usuario no encontrado al intentar promover (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario a promover no encontrado")
    
    if user.is_admin:
        logger.info("Usuario ya es admin, no se requiere acción (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
        return {"detail": "El usuario ya es administrador"}

    user.is_admin = True
    db.commit()
    logger.info("Usuario promovido a admin exitosamente (admin)", target_user_id=user_id, admin_user_id=admin_user_id)
    return {"detail": "Promocionado a admin"}
