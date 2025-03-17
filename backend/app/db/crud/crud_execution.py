from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from ...models.execution import Execution, ExecutionOutput
from ...schemas.execution import ExecutionCreate, ExecutionUpdate, ExecutionOutputCreate

def get_execution(db: Session, execution_id: str) -> Optional[Execution]:
    """
    通过ID获取执行记录
    
    Args:
        db: 数据库会话
        execution_id: 执行ID
        
    Returns:
        Optional[Execution]: 执行记录对象，如果不存在则返回None
    """
    return db.query(Execution).filter(Execution.id == execution_id).first()

def get_executions_by_conversation(db: Session, conversation_id: str, skip: int = 0, limit: int = 100) -> List[Execution]:
    """
    获取指定对话的所有执行记录
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        skip: 跳过的记录数
        limit: 返回的最大记录数
        
    Returns:
        List[Execution]: 执行记录列表
    """
    return db.query(Execution).filter(
        Execution.conversation_id == conversation_id
    ).order_by(Execution.created_at.desc()).offset(skip).limit(limit).all()

def create_execution(db: Session, obj_in: ExecutionCreate) -> Execution:
    """
    创建新执行记录
    
    Args:
        db: 数据库会话
        obj_in: 执行记录创建模型
        
    Returns:
        Execution: 创建的执行记录对象
    """
    db_obj = Execution(
        id=obj_in.id,
        conversation_id=obj_in.conversation_id,
        code=obj_in.code,
        language=obj_in.language,
        status=obj_in.status,
        created_at=obj_in.created_at,
        updated_at=obj_in.updated_at
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def update_execution(db: Session, db_obj: Execution, obj_in: ExecutionUpdate) -> Execution:
    """
    更新执行记录
    
    Args:
        db: 数据库会话
        db_obj: 数据库中的执行记录对象
        obj_in: 执行记录更新模型
        
    Returns:
        Execution: 更新后的执行记录对象
    """
    update_data = obj_in.dict(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_execution(db: Session, execution_id: str) -> bool:
    """
    删除执行记录
    
    Args:
        db: 数据库会话
        execution_id: 执行ID
        
    Returns:
        bool: 删除是否成功
    """
    execution = get_execution(db, execution_id)
    if not execution:
        return False
    
    # 先删除相关的输出记录
    delete_outputs_by_execution(db, execution_id)
    
    db.delete(execution)
    db.commit()
    return True

def delete_executions_by_conversation(db: Session, conversation_id: str) -> int:
    """
    删除指定对话的所有执行记录
    
    Args:
        db: 数据库会话
        conversation_id: 对话ID
        
    Returns:
        int: 删除的执行记录数量
    """
    executions = get_executions_by_conversation(db, conversation_id)
    count = len(executions)
    
    for execution in executions:
        # 先删除相关的输出记录
        delete_outputs_by_execution(db, execution.id)
        db.delete(execution)
    
    db.commit()
    return count

# 执行输出相关操作

def get_execution_output(db: Session, output_id: str) -> Optional[ExecutionOutput]:
    """
    通过ID获取执行输出
    
    Args:
        db: 数据库会话
        output_id: 输出ID
        
    Returns:
        Optional[ExecutionOutput]: 执行输出对象，如果不存在则返回None
    """
    return db.query(ExecutionOutput).filter(ExecutionOutput.id == output_id).first()

def get_outputs_by_execution(db: Session, execution_id: str) -> List[ExecutionOutput]:
    """
    获取指定执行记录的所有输出
    
    Args:
        db: 数据库会话
        execution_id: 执行ID
        
    Returns:
        List[ExecutionOutput]: 执行输出列表
    """
    return db.query(ExecutionOutput).filter(
        ExecutionOutput.execution_id == execution_id
    ).order_by(ExecutionOutput.timestamp.asc()).all()

def create_execution_output(db: Session, obj_in: ExecutionOutputCreate) -> ExecutionOutput:
    """
    创建新执行输出
    
    Args:
        db: 数据库会话
        obj_in: 执行输出创建模型
        
    Returns:
        ExecutionOutput: 创建的执行输出对象
    """
    db_obj = ExecutionOutput(
        id=obj_in.id,
        execution_id=obj_in.execution_id,
        output_type=obj_in.output_type,
        content=obj_in.content,
        timestamp=obj_in.timestamp
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def delete_outputs_by_execution(db: Session, execution_id: str) -> int:
    """
    删除指定执行记录的所有输出
    
    Args:
        db: 数据库会话
        execution_id: 执行ID
        
    Returns:
        int: 删除的输出数量
    """
    outputs = get_outputs_by_execution(db, execution_id)
    count = len(outputs)
    
    for output in outputs:
        db.delete(output)
    
    db.commit()
    return count