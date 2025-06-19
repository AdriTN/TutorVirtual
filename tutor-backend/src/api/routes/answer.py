from src.api.schemas.answer import AnswerOut, AnswerIn
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.models import Exercise
from src.services.exercise_service import register_user_answer

router = APIRouter()


@router.post("", response_model=AnswerOut, status_code=201,
             dependencies=[Depends(jwt_required)])
def answer(body:AnswerIn,
           payload:dict = Depends(jwt_required),
           db:Session  = Depends(get_db)):
    user_id = payload["user_id"]
    ej = db.query(Exercise).get(body.ejercicio_id)
    if not ej:
        raise HTTPException(404,"Ejercicio no encontrado")

    ok = register_user_answer(user_id, ej, body.answer, body.tiempo_seg, db)
    return AnswerOut(correcto=ok)
