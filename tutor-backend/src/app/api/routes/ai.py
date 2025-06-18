from json import JSONDecodeError, loads
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from ...database.session import get_db
from ...api.dependencies.auth import jwt_required
from ...api.schemas.ai import RawOllamaRequest, AIExerciseOut
from ...models import Exercise, Theme
from ...services.exercise_service import create_exercise_from_ai
from ...utils.ollama_client import generate_with_ollama

router = APIRouter()


# ────────── Endpoint ──────────
@router.post(
    "/request",
    response_model=AIExerciseOut,
    status_code=status.HTTP_200_OK,
)
def ask_ollama(
    req: RawOllamaRequest,
    _: dict = Depends(jwt_required),
    db: Session = Depends(get_db),
):
    try:
        raw = generate_with_ollama(req.dict())
    except httpx.HTTPError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Ollama: {exc}")

    try:
        data = loads(raw["choices"][0]["message"]["content"])
    except (KeyError, JSONDecodeError):
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Respuesta AI inválida")

    tema: Theme | None = (
        db.query(Theme)
        .filter(func.lower(Theme.name) == data["tema"].strip().lower())
        .first()
    )
    if not tema:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Tema no encontrado")

    ej: Exercise = create_exercise_from_ai(data, tema, db)

    return AIExerciseOut(
        id=ej.id,
        tema=tema.name,
        enunciado=ej.statement,
        dificultad=ej.difficulty,
        tipo=ej.type,
        explicacion=ej.explanation,
    )
