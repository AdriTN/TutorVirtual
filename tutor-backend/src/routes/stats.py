from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from dependencies.database_dependencies import get_db
from dependencies.auth_dependencies import jwt_required
import services.stats_service as stats_service

router = APIRouter(
    prefix="/stats",
    tags=["Stats"],
    dependencies=[Depends(jwt_required)]
)

@router.get("/overview")
def overview(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return stats_service.overview(db, payload["user_id"])

@router.get("/timeline")
def timeline(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return stats_service.timeline(db, payload["user_id"])

@router.get("/by-theme")
def by_theme(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return stats_service.by_theme(db, payload["user_id"])
