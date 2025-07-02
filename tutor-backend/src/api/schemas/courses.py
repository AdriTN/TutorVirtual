from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List, Optional


# ---------- Salida ----------
class ThemeOut(BaseModel):
    id: int
    title: str
    description: str | None
    subject_id: int

    model_config = {"from_attributes": True}


class SubjectOut(BaseModel):
    id: int
    name: str
    description: str | None = None
    enrolled: bool
    themes: list[ThemeOut]

    model_config = {"from_attributes": True}


class CourseOut(BaseModel):
    id: int
    title: str
    description: str | None = None
    subjects: list[SubjectOut]

    model_config = {"from_attributes": True}


# ---------- Entrada ----------
class CourseIn(BaseModel):
    title: str = Field(..., min_length=3)
    description: str | None = None
    subject_ids: list[int] | None = None

    model_config = dict(
        json_schema_extra={
            "example": {
                "title": "1º ESO",
                "description": "Curso completo de primero de ESO",
                "subject_ids": [1, 2, 5],
            }
        }
    )

class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    subject_ids: Optional[List[int]] = None


class SubjectDetach(BaseModel):
    subject_ids: List[int]
