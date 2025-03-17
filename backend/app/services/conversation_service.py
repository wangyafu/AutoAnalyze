from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from ..db.session import get_db
from ..db.crud import crud_conversation, crud_message
from ..schemas.conversation import ConversationCreate, ConversationResponse
from ..schemas.message import MessageCreate, MessageResponse
from sqlalchemy.orm import Session

def get_conversations(limit: int = 10, offset: int = 0, db: Session = None) -> Dict[str, Any]:
    """
    获取对话列表
    
    Args:
        limit: 返回的最大对话数
        offset: 分页偏移量
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 包含总数和对话列表的字典
    """
    if db is None:
        db = next(get_db())
    
    # 获取对话总数
    total = crud_conversation.get_count(db)
    
    # 获取对话列表
    conversations = crud_conversation.get_multi(db, skip=offset, limit=limit)
    
    return {
        "total": total,
        "conversations": conversations
    }

def get_conversation(conversation_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
    """
    获取对话详情
    
    Args:
        conversation_id: 对话ID
        db: 数据库会话
        
    Returns:
        Optional[Dict[str, Any]]: 对话详情，包括消息列表
    """
    if db is None:
        db = next(get_db())
    
    # 获取对话
    conversation = crud_conversation.get(db, conversation_id)
    if not conversation:
        return None
    
    # 获取对话的消息
    messages = crud_message.get_by_conversation(db, conversation_id)
    
    # 构建响应
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "messages": messages
    }

def create_conversation(title: str, db: Session = None) -> Dict[str, Any]:
    """
    创建对话
    
    Args:
        title: 对话标题
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 创建的对话信息
    """
    if db is None:
        db = next(get_db())
    
    # 生成对话ID
    conversation_id = f"conv_{uuid4().hex[:8]}"
    
    # 创建对话
    conversation_data = ConversationCreate(
        id=conversation_id,
        title=title,
        created_at=datetime.now()
    )
    
    # 保存到数据库
    conversation = crud_conversation.create(db, obj_in=conversation_data)
    
    return {
        "id": conversation.id,
        "title": conversation.title,
        "created_at": conversation.created_at
    }

def delete_conversation(conversation_id: str, db: Session = None) -> bool:
    """
    删除对话
    
    Args:
        conversation_id: 对话ID
        db: 数据库会话
        
    Returns:
        bool: 删除是否成功
    """
    if db is None:
        db = next(get_db())
    
    # 检查对话是否存在
    conversation = crud_conversation.get(db, conversation_id)
    if not conversation:
        return False
    
    # 删除对话相关的消息
    crud_message.delete_by_conversation(db, conversation_id)
    
    # 删除对话
    crud_conversation.remove(db, id=conversation_id)
    
    return True

def add_message(conversation_id: str, role: str, content: str, db: Session = None) -> Optional[Dict[str, Any]]:
    """
    添加消息
    
    Args:
        conversation_id: 对话ID
        role: 消息角色 (user/assistant)
        content: 消息内容
        db: 数据库会话
        
    Returns:
        Optional[Dict[str, Any]]: 添加的消息信息
    """
    if db is None:
        db = next(get_db())
    
    # 检查对话是否存在
    conversation = crud_conversation.get(db, conversation_id)
    if not conversation:
        return None
    
    # 生成消息ID
    message_id = f"msg_{uuid4().hex[:8]}"
    
    # 创建消息
    message_data = MessageCreate(
        id=message_id,
        conversation_id=conversation_id,
        role=role,
        content=content,
        timestamp=datetime.now()
    )
    
    # 保存到数据库
    message = crud_message.create(db, obj_in=message_data)
    
    return {
        "id": message.id,
        "conversation_id": message.conversation_id,
        "role": message.role,
        "content": message.content,
        "timestamp": message.timestamp
    }