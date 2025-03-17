from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Integer, Enum
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
import enum

from ..db.session import Base


class ExecutionStatus(str, enum.Enum):
    """执行状态枚举
    
    定义代码执行的可能状态
    """
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 执行被取消


class Execution(Base):
    """执行记录模型
    
    存储代码执行的记录信息
    """
    __tablename__ = "executions"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    code = Column(Text)  # 执行的代码内容
    language = Column(String)  # 代码语言
    status = Column(String, default=ExecutionStatus.PENDING)  # 执行状态
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)  # 开始执行时间
    completed_at = Column(DateTime, nullable=True)  # 完成执行时间
    
    # 关系：执行记录属于一个对话
    conversation = relationship("Conversation", back_populates="executions")
    
    # 关系：一个执行记录有多个输出
    outputs = relationship("ExecutionOutput", back_populates="execution", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Execution(id={self.id}, status={self.status}, conversation_id={self.conversation_id})>"


class ExecutionOutput(Base):
    """执行输出模型
    
    存储代码执行的输出内容
    """
    __tablename__ = "execution_outputs"
    
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    execution_id = Column(String, ForeignKey("executions.id", ondelete="CASCADE"), index=True)
    output_type = Column(String, index=True)  # 'stdout', 'stderr', 'result', 'error'
    content = Column(Text)  # 输出内容
    sequence = Column(Integer, index=True)  # 输出序号，用于排序
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系：输出属于一个执行记录
    execution = relationship("Execution", back_populates="outputs")
    
    def __repr__(self):
        return f"<ExecutionOutput(id={self.id}, type={self.output_type}, execution_id={self.execution_id})>"