# src/routes/ai.py
import json
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, List
import httpx
from pydantic import BaseModel, Field
from ..utils.ollama_client import generate_with_ollama
from ..dependencies.auth_dependencies import jwt_required

router = APIRouter(prefix="/ai", tags=["IA"])

class RawOllamaRequest(BaseModel):
    model: str
    response_format: Dict[str,Any]
    messages: List[Dict[str,Any]]
    
class AIExercise(BaseModel):
    tema: str
    enunciado: str
    respuesta: str
    dificultad: str
    tipo: str
    explicacion: str

@router.post(
    "/ask",
    response_model=AIExercise,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(jwt_required)]
)
def ask_ollama(req: RawOllamaRequest):
    payload = req.dict()
    try:
        raw = generate_with_ollama(payload)
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error al conectar con Ollama: {e}"
        )
    # Extraemos contenido
    try:
        content_str = raw["choices"][0]["message"]["content"]
        data = json.loads(content_str)
    except Exception as e:
        raise HTTPException(500, f"Error parseando respuesta de Ollama: {e}")

    # ahora devuelves un dict que FastAPI convierte al modelo AIExercise
    return AIExercise(**data)
