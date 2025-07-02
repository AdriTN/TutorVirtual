from pydantic import BaseModel
from datetime import datetime
from typing import List

class ChatMessageBase(BaseModel):
    message: str

class ChatMessageCreate(ChatMessageBase):
    sender_type: str  # "user" or "ai"

class ChatMessageResponse(ChatMessageBase):
    id: int
    conversation_id: int
    sender_type: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatConversationBase(BaseModel):
    user_id: int
    exercise_id: int

class ChatConversationCreate(ChatConversationBase):
    pass

class ChatConversationResponse(ChatConversationBase):
    id: int
    created_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True

from typing import Optional

class UserMessageInput(BaseModel):
    message: str
    exercise_id: int # To identify or create the conversation
    conversation_id: Optional[int] = None # Optional: if a conversation already exists
