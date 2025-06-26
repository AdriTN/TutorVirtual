from typing import Optional
from pydantic import BaseModel, Field


class ThemeUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    subject_id: Optional[int] = None