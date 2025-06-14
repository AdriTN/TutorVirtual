from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...api.dependencies.auth import jwt_required
from ...models import Exercise
from ...services.exercise_service import register_user_answer

router = APIRouter(prefix="/answer", tags=["Answer"])


class AnswerIn(BaseModel):
    ejercicio_id: int
    respuesta: str
    tiempo_seg: int | None = None


class AnswerOut(BaseModel):
    correcto: bool


@router.post("", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
def answer(
    body: AnswerIn,
    payload: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    ej: Exercise | None = db.query(Exercise).get(body.ejercicio_id)
    if not ej:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Ejercicio no encontrado")

    ok = register_user_answer(
        payload["user_id"], ej, body.respuesta, body.tiempo_seg, db
    )
    return AnswerOut(correcto=ok)
