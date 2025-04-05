from typing import List, Optional, Dict, Any
from uuid import uuid4
from datetime import datetime
from ..schemas.conversation import ConversationCreate
from sqlalchemy.orm import Session


def create_conversation(title: str, db: Session = None) -> Dict[str, Any]:
    """
    创建对话
    
    Args:
        title: 对话标题
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 创建的对话信息
    """
 
    
    # 生成对话ID
    conversation_id = f"conv_{uuid4().hex[:8]}"
    
    # 创建对话
    conversation_data = ConversationCreate(
        id=conversation_id,
        title=title,
        created_at=datetime.now()
    )
    
    # # 保存到数据库
    # conversation = crud_conversation.create(db, obj_in=conversation_data)
    
    return {
        "id": conversation_id,
        "title": title,
        "created_at": datetime.now()
    }

