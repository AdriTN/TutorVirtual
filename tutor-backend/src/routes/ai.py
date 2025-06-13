# src/routes/ai.py
import json
from dependencies.database_dependencies import get_db
from fastapi import APIRouter, Depends, HTTPException, status


from typing import Any, Dict, List
import httpx
from models.exercises import Ejercicio
from models.thems import Tema
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..utils.ollama_client import generate_with_ollama
from ..dependencies.auth_dependencies import jwt_required

class RawOllamaRequest(BaseModel):
    model: str
    response_format: Dict[str, Any]
    messages: List[Dict[str, Any]]


class AIExerciseOut(BaseModel):
    id: int
    tema: str
    enunciado: str
    dificultad: str
    tipo: str
    explicacion: str | None = None

router = APIRouter(prefix="/ai")

@router.post(
    "/request",
    response_model=AIExerciseOut,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(jwt_required)],
)
def ask_ollama(req: RawOllamaRequest, db: Session = Depends(get_db)):
    #
    # 1) Llamar a Ollama
    #
    try:
        raw = generate_with_ollama(req.dict())
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")

    #
    # 2) Parsear JSON devuelto
    #
    try:
        data = json.loads(raw["choices"][0]["message"]["content"])
    except (KeyError, json.JSONDecodeError) as e:
        raise HTTPException(500, f"Respuesta de Ollama no válida: {e}")

    #
    # 3) Relacionar con Tema y guardar Ejercicio
    #
    buscado = data["tema"].strip()
    tema = (
    db.query(Tema)
      .filter(func.lower(Tema.nombre) == buscado.lower())  # insensible a mayúsculas
      .first()
)
    print(f"Buscando tema: {data['tema']} -> {tema}")
    if not tema:
        raise HTTPException(404, "Tema no encontrado")

    ej = Ejercicio(
        enunciado=data["enunciado"],
        tipo=data["tipo"],
        dificultad=data["dificultad"],
        respuesta=data["respuesta"],
        explicacion=data.get("explicacion"),
        tema_id=tema.id,
    )
    db.add(ej)
    db.commit()
    db.refresh(ej)

    #
    # 4) Devolver DTO (sin la solución «respuesta»)
    #
    return AIExerciseOut(
        id=ej.id,
        tema=tema.nombre,
        enunciado=ej.enunciado,
        dificultad=ej.dificultad,
        tipo=ej.tipo,
        explicacion=ej.explicacion,
    )