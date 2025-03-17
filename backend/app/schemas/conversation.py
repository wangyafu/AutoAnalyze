from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class ConversationBase(BaseModel):
    """对话基础模式"""
    title: str = Field(..., description="对话标题")


class ConversationCreate(ConversationBase):
    """创建对话请求"""
    pass


class ConversationResponse(ConversationBase):
    """对话响应"""
    id: str = Field(..., description="对话ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    message_count: Optional[int] = Field(0, description="消息数量")

    class Config:
        orm_mode = True


class ConversationDetail(ConversationResponse):
    """对话详情响应，包含消息列表"""
    messages: List["MessageResponse"] = Field([], description="消息列表")

    class Config:
        orm_mode = True


class ConversationList(BaseModel):
    """对话列表响应"""
    conversations: List[ConversationResponse] = Field([], description="对话列表")
    total: int = Field(..., description="总数")
    offset: int = Field(..., description="偏移量")
    limit: int = Field(..., description="限制数量")

    class Config:
        orm_mode = True