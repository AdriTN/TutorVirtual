from typing import List, Optional
from pydantic import BaseModel, Field


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class ThemeDetach(BaseModel):
    theme_ids: List[int]
    
class SubjectEnrollData(BaseModel):
    course_id: int