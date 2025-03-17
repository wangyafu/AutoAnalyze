from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageBase(BaseModel):
    """消息基础模式"""
    role: str = Field(..., description="消息角色，'user'或'assistant'")
    content: str = Field(..., description="消息内容")


class MessageCreate(MessageBase):
    """创建消息请求"""
    conversation_id: str = Field(..., description="对话ID")
    id: str = Field(..., description="消息ID")
    timestamp: datetime = Field(..., description="创建时间")


class MessageUpdate(BaseModel):
    """更新消息请求"""
    content: Optional[str] = Field(None, description="消息内容")
    role: Optional[str] = Field(None, description="消息角色")


class MessageResponse(MessageBase):
    """消息响应"""
    id: str = Field(..., description="消息ID")
    conversation_id: str = Field(..., description="对话ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        orm_mode = True


class UserMessage(BaseModel):
    """用户消息"""
    content: str = Field(..., description="消息内容")
    conversation_id: Optional[str] = Field(None, description="对话ID，如果为None则创建新对话")


class AssistantMessage(BaseModel):
    """助手消息"""
    content: str = Field(..., description="消息内容")
    conversation_id: str = Field(..., description="对话ID")
    created_at: datetime = Field(..., description="创建时间")