from json import JSONDecodeError, loads
from typing import Any, Dict, List

import httpx
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.api.dependencies.auth import jwt_required
from src.api.schemas.ai import RawOllamaRequest, AIExerciseOut
from src.models import Exercise, Theme
from src.services.exercise_service import create_exercise_from_ai
from src.utils.ollama_client import generate_with_ollama

router = APIRouter()
logger = structlog.get_logger(__name__)


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
    logger.info("Recibida solicitud POST en /api/ai/request", request_data=req.dict(exclude_none=True))
    logger.info("Solicitud a Ollama iniciada", model=req.model, num_messages=len(req.messages) if req.messages else 0)
    try:
        raw = generate_with_ollama(req.dict())
    except httpx.HTTPError as exc:
        logger.error("Error de comunicación con Ollama", detail=str(exc), exc_info=exc)
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"Ollama: {exc}")

    try:
        content_str = raw["choices"][0]["message"]["content"]
        if content_str.startswith("```json\n"):
            content_str = content_str[len("```json\n"):-len("\n```")]
        elif content_str.startswith("```\n"):
             content_str = content_str[len("```\n"):-len("\n```")]

        data = loads(content_str)
    except (KeyError, JSONDecodeError, TypeError) as e:
        logger.error("Respuesta de Ollama inválida o malformada", raw_response=raw, error_message=str(e), exc_info=True)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Respuesta AI inválida")

    tema_solicitado = data.get("tema", "N/A").strip().lower()
    tema: Theme | None = (
        db.query(Theme)
        .filter(func.lower(Theme.name) == tema_solicitado)
        .first()
    )
    if not tema:
        logger.warn("Tema no encontrado en la base de datos", tema_solicitado=tema_solicitado, available_themes=[t.name for t in db.query(Theme.name).all()])
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Tema '{data.get('tema', 'N/A')}' no encontrado")

    ej: Exercise = create_exercise_from_ai(data, tema, db)
    logger.info("Ejercicio creado desde respuesta de AI", exercise_id=ej.id, theme_id=tema.id, theme_name=tema.name)

    return AIExerciseOut(
        id=ej.id,
        tema=tema.name,
        enunciado=ej.statement,
        dificultad=ej.difficulty,
        tipo=ej.type,
        explicacion=ej.explanation,
    )
