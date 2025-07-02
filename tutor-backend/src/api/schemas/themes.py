from typing import Optional
from pydantic import BaseModel, Field


class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    subject_id: Optional[int] = None


class ThemeCreate(BaseModel):
    name: str = Field(..., max_length=255, examples=["Introducción a las Ecuaciones"])
    description: Optional[str] = Field(None, examples=["Conceptos básicos y tipos de ecuaciones."])
    subject_id: int = Field(..., examples=[1])

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Tema de Ejemplo",
                "description": "Una breve descripción del tema.",
                "subject_id": 1,
            }
        }