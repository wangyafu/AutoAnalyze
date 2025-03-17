from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ...models.message import Message
from ...schemas.message import MessageCreate, MessageUpdate

def get(db: Session, message_id: str) -> Optional[Message]:
    """
    通过ID获取消息
    
    Args:
        db: 数据库会话
        message_id: 消息ID
        
    Returns:
        Optional[Message]: 消息对象，如果不存在则返回None
    """
    return db.query(Message).filter(Message.id == message_id).first()

def get_by_conversation(db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
    """
    获取指定对话的所有消息
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[Message]: 消息列表
    """
    return db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.timestamp.asc()).offset(skip).limit(limit).all()

def create(db: Session, obj_in: MessageCreate) -> Message:
    """
    创建新消息
    
    Args:
        db: 数据库会话
        obj_in: 消息创建模型
        
    Returns:
        Message: 创建的消息对象
    """
    db_obj = Message(
        id=obj_in.id,
        conversation_id=obj_in.conversation_id,
        role=obj_in.role,
        content=obj_in.content,
        timestamp=obj_in.timestamp
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update(db: Session, db_obj: Message, obj_in: MessageUpdate) -> Message:
    """
    更新消息
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的消息对象
        obj_in: 消息更新模型
        
    Returns:
        Message: 更新后的消息对象
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete(db: Session, message_id: str) -> bool:
    """
    删除消息
    
    Args:
        db: 数据库会话
        message_id: 消息ID
        
    Returns:
        bool: 删除是否成功
    """
    message = get(db, message_id)
    if not message:
        return False
    
    db.delete(message)
    db.commit()
    return True

def delete_by_conversation(db: Session, conversation_id: str) -> int:
    """
    删除指定对话的所有消息
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        
    Returns:
        int: 删除的消息数量
    """
    messages = get_by_conversation(db, conversation_id)
    count = len(messages)
    
    for message in messages:
        db.delete(message)
    
    db.commit()
    return count

def get_count_by_conversation(db: Session, conversation_id: str) -> int:
    """
    获取指定对话的消息数量
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        
    Returns:
        int: 消息数量
    """
    return db.query(Message).filter(Message.conversation_id == conversation_id).count()