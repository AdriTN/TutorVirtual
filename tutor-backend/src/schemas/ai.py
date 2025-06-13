from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Message(BaseModel):
    role: str = Field(..., regex="^(user|assistant|system)$")
    content: str

class AskRequest(BaseModel):
    model: str
    response_format: Dict[str,Any]
    messages: List[Message] = Field(..., min_items=1)

class AskResponse(BaseModel):
    content: str
