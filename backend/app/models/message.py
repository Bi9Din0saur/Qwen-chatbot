from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from .base import Base

class MessageType(str, enum.Enum):
    user = "user"
    bot = "bot"

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String(50), primary_key=True, index=True)
    chat_session_id = Column(String(50), ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=True)  # 文本内容
    type = Column(Enum(MessageType), nullable=False)
    image_url = Column(String(500), nullable=True)  # 图片URL
    image_path = Column(String(500), nullable=True)  # 本地图片路径
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    chat_session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id='{self.id}', type='{self.type}', content='{self.content[:50]}...')>"
