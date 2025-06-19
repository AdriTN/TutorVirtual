from typing import Any, Dict, List
from pydantic import BaseModel


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
