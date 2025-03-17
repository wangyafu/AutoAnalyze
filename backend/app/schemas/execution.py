from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import enum


class ExecutionStatus(str, enum.Enum):
    """执行状态枚举"""
    PENDING = "pending"  # 等待执行
    RUNNING = "running"  # 正在执行
    COMPLETED = "completed"  # 执行完成
    FAILED = "failed"  # 执行失败
    CANCELLED = "cancelled"  # 执行被取消


class ExecutionRequest(BaseModel):
    """执行请求"""
    code: str = Field(..., description="要执行的代码")
    language: str = Field("python", description="代码语言")
    conversation_id: str = Field(..., description="关联的对话ID")


class ExecutionCreate(BaseModel):
    """执行记录创建模型"""
    id: str = Field(..., description="执行ID")
    conversation_id: str = Field(..., description="关联的对话ID")
    code: str = Field(..., description="执行的代码")
    language: str = Field("python", description="代码语言")
    status: ExecutionStatus = Field(ExecutionStatus.PENDING, description="执行状态")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ExecutionUpdate(BaseModel):
    """执行记录更新模型"""
    status: Optional[ExecutionStatus] = Field(None, description="执行状态")
    started_at: Optional[datetime] = Field(None, description="开始执行时间")
    completed_at: Optional[datetime] = Field(None, description="完成执行时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class ExecutionResponse(BaseModel):
    """执行响应"""
    id: str = Field(..., description="执行ID")
    status: ExecutionStatus = Field(..., description="执行状态")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始执行时间")
    completed_at: Optional[datetime] = Field(None, description="完成执行时间")
    conversation_id: str = Field(..., description="关联的对话ID")

    class Config:
        orm_mode = True


class ExecutionOutputType(str, enum.Enum):
    """执行输出类型枚举"""
    STDOUT = "stdout"  # 标准输出
    STDERR = "stderr"  # 标准错误
    RESULT = "result"  # 执行结果
    ERROR = "error"  # 执行错误


class ExecutionOutputCreate(BaseModel):
    """执行输出创建模型"""
    id: str = Field(..., description="输出ID")
    execution_id: str = Field(..., description="关联的执行ID")
    output_type: str = Field(..., description="输出类型")
    content: str = Field(..., description="输出内容")
    timestamp: datetime = Field(..., description="创建时间")


class ExecutionOutput(BaseModel):
    """执行输出"""
    id: str = Field(..., description="输出ID")
    execution_id: str = Field(..., description="关联的执行ID")
    output_type: str = Field(..., description="输出类型")
    content: str = Field(..., description="输出内容")
    sequence: int = Field(..., description="输出序号")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        orm_mode = True


class CancelExecutionRequest(BaseModel):
    """取消执行请求"""
    execution_id: str = Field(..., description="要取消的执行ID")


class ExecutionStatusResponse(BaseModel):
    """执行状态响应"""
    status: ExecutionStatus = Field(..., description="执行状态")
    outputs: List[ExecutionOutput] = Field([], description="执行输出列表")

    class Config:
        orm_mode = True