from dependencies.auth_dependencies import jwt_required
from dependencies.database_dependencies import get_db
from models.exercises import Ejercicio
from pydantic import BaseModel
from pytest import Session
from services.exercise_service import register_user_answer
from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/answer", tags=["Answer"])

class AnswerIn(BaseModel):
    ejercicio_id: int
    respuesta   : str
    tiempo_seg  : int | None = None

class AnswerOut(BaseModel):
    correcto: bool

@router.post("", response_model=AnswerOut, status_code=201,
             dependencies=[Depends(jwt_required)])
def answer(body:AnswerIn,
           payload:dict = Depends(jwt_required),
           db:Session  = Depends(get_db)):
    user_id = payload["user_id"]
    ej = db.query(Ejercicio).get(body.ejercicio_id)
    if not ej:
        raise HTTPException(404,"Ejercicio no encontrado")

    ok = register_user_answer(user_id, ej, body.respuesta, body.tiempo_seg, db)
    return AnswerOut(correcto=ok)
