from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.services import stats_service as svc

router = APIRouter()


@router.get("/overview")
def overview(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return svc.overview(db, payload["user_id"])


@router.get("/timeline")
def timeline(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return svc.timeline(db, payload["user_id"])


@router.get("/by-theme")
def by_theme(db: Session = Depends(get_db), payload: dict = Depends(jwt_required)):
    return svc.by_theme(db, payload["user_id"])
