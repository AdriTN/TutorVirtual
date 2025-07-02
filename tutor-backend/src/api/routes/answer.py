import structlog
from src.api.schemas.answer import AnswerOut, AnswerIn
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.models import Exercise
from src.services.exercise_service import register_user_answer

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.post("", response_model=AnswerOut, status_code=201,
             dependencies=[Depends(jwt_required)])
def answer(body:AnswerIn,
           payload:dict = Depends(jwt_required),
           db:Session  = Depends(get_db)):
    user_id = payload["user_id"]
    logger.info(
        "Procesando respuesta de usuario",
        user_id=user_id,
        exercise_id=body.ejercicio_id,
        answer=body.answer,
        time_taken_seconds=body.tiempo_seg,
    )

    ej = db.query(Exercise).get(body.ejercicio_id)
    if not ej:
        logger.warn("Ejercicio no encontrado al procesar respuesta", exercise_id=body.ejercicio_id, user_id=user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejercicio no encontrado")

    ok = register_user_answer(user_id, ej, body.answer, body.tiempo_seg, db)
    logger.info("Respuesta registrada", user_id=user_id, exercise_id=ej.id, is_correct=ok)

    response_data = {"correcto": ok}
    if not ok:
        response_data["correct_answer"] = ej.answer
    if ej.explanation:
        response_data["explanation"] = ej.explanation

    return AnswerOut(**response_data)
