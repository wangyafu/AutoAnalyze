from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.schemas.conversation import ConversationCreate, ConversationResponse, ConversationDetail, ConversationList
from app.services.conversation_service import get_conversations, get_conversation, create_conversation, delete_conversation
from typing import List, Optional
import uuid

# 创建路由实例
router = APIRouter()


@router.get("", response_model=ConversationList)
async def list_conversations(limit: int = Query(20, description="每页数量"),
                            offset: int = Query(0, description="偏移量")):
    """获取对话列表"""
    try:
        conversations, total = get_conversations(limit, offset)
        return ConversationList(
            conversations=conversations,
            total=total,
            offset=offset,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=ConversationResponse)
async def create_new_conversation(conversation: ConversationCreate):
    """创建新对话"""
    try:
        new_conversation = create_conversation(conversation.title)
        return new_conversation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation_detail(conversation_id: str = Path(..., description="对话ID")):
    """获取对话详情"""
    try:
        conversation = get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="对话不存在")
        return conversation
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{conversation_id}", response_model=dict)
async def delete_conversation_by_id(conversation_id: str = Path(..., description="对话ID")):
    """删除对话"""
    try:
        success = delete_conversation(conversation_id)
        if not success:
            raise HTTPException(status_code=404, detail="对话不存在")
        return {"status": "success", "message": "对话已删除"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))