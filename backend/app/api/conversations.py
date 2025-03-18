from fastapi import APIRouter, Depends, HTTPException, Query, Path
from app.schemas.conversation import ConversationCreate, ConversationResponse
from app.services.conversation_service import create_conversation
from typing import List, Optional
import uuid
from app.utils.logger import get_logger
# 创建路由实例
router = APIRouter()
logger=get_logger(__name__)


@router.post("", response_model=ConversationResponse)
async def create_new_conversation(conversation: ConversationCreate):
    """创建新对话"""
    try:
        new_conversation = create_conversation(conversation.title)
        return new_conversation
    except Exception as e:
        logger.error(f"create_new_conversation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
