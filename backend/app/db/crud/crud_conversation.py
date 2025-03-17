from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import uuid4

from app.models.conversation import Conversation


def get_conversations(db: Session, skip: int = 0, limit: int = 100) -> List[Conversation]:
    """获取对话列表
    
    Args:
        db: 数据库会话
        skip: 跳过记录数
        limit: 返回记录数上限
        
    Returns:
        对话列表
    """
    return db.query(Conversation).order_by(Conversation.updated_at.desc()).offset(skip).limit(limit).all()


def get_conversation(db: Session, conversation_id: str) -> Optional[Conversation]:
    """获取单个对话
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        
    Returns:
        对话对象，如果不存在则返回None
    """
    return db.query(Conversation).filter(Conversation.id == conversation_id).first()


def create_conversation(db: Session, title: str) -> Conversation:
    """创建新对话
    
    Args:
        db: 数据库会话
        title: 对话标题
        
    Returns:
        新创建的对话对象
    """
    db_conversation = Conversation(id=str(uuid4()), title=title)
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation


def update_conversation(db: Session, conversation_id: str, title: str) -> Optional[Conversation]:
    """更新对话
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        title: 新的对话标题
        
    Returns:
        更新后的对话对象，如果不存在则返回None
    """
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db_conversation.title = title
        db.commit()
        db.refresh(db_conversation)
    return db_conversation


def delete_conversation(db: Session, conversation_id: str) -> bool:
    """删除对话
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        
    Returns:
        是否成功删除
    """
    db_conversation = get_conversation(db, conversation_id)
    if db_conversation:
        db.delete(db_conversation)
        db.commit()
        return True
    return False