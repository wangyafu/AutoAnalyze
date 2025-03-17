from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..db.session import Base


class Conversation(Base):
    """对话模型
    
    存储用户与系统之间的对话会话信息
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系：一个对话有多条消息
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # 关系：一个对话有多个执行记录
    executions = relationship("Execution", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"