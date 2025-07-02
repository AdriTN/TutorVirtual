from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator

# ── Tipos anotados reutilizables ───────────────────────────────────────────────
PositiveId = Annotated[int, Field(gt=0, description="Identificador positivo")]

# ── Schemas de entrada / salida ────────────────────────────────────────────────
class AnswerIn(BaseModel):
    """Cuerpo del POST /answer"""

    ejercicio_id: PositiveId
    answer:   str = Field(min_length=1, strip_whitespace=True)
    tiempo_seg:  int | None = Field(
        default=None,
        ge=0,
        description="Segundos empleados (opcional, ≥ 0)",
    )

    @field_validator("answer")
    @classmethod
    def _respuesta_no_vacia(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La respuesta no puede estar vacía")
        return v.strip()

    model_config = dict(
        json_schema_extra={
            "example": {
                "ejercicio_id": 42,
                "answer": "4",
                "tiempo_seg": 15,
            }
        }
    )


class AnswerOut(BaseModel):
    """Respuesta HTTP"""

    correcto: bool
    correct_answer: str | None = None
    explanation: str | None = None
