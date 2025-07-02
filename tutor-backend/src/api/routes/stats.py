import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.services import stats_service as svc

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/overview")
def overview(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    user_id = payload["user_id"]
    logger.info("Solicitando estadísticas generales (overview)", user_id=user_id)
    result = svc.overview(db, user_id)
    logger.info("Estadísticas generales (overview) generadas", user_id=user_id, result_keys=list(result.keys()) if isinstance(result, dict) else None)
    return result


@router.get("/timeline")
def timeline(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    user_id = payload["user_id"]
    logger.info("Solicitando línea de tiempo de estadísticas (timeline)", user_id=user_id)
    result = svc.timeline(db, user_id)
    logger.info("Línea de tiempo de estadísticas (timeline) generada", user_id=user_id, num_entries=len(result) if isinstance(result, list) else None)
    return result


@router.get("/by-theme")
def by_theme(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    user_id = payload["user_id"]
    logger.info("Solicitando estadísticas por tema (by-theme)", user_id=user_id)
    result = svc.by_theme(db, user_id)
    logger.info("Estadísticas por tema (by-theme) generadas", user_id=user_id, num_themes=len(result) if isinstance(result, list) else None)
    return result
