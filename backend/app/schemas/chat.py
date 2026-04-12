from pydantic import BaseModel
from datetime import datetime
import uuid

class ConversationCreate(BaseModel):
    title: str = "New Conversation"

class ConversationResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    conversation_id: uuid.UUID
    message: str