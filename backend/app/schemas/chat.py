from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from ..models.message import MessageType

class MessageBase(BaseModel):
    content: Optional[str] = None
    type: MessageType
    image_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: str
    chat_session_id: str
    timestamp: datetime
    image_path: Optional[str] = None

    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: str

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    image_url: Optional[str] = None
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    usage: Optional[dict] = None
