from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from app.db.session import get_db
from app.db.crud import crud_execution
from app.schemas.execution import ExecutionCreate, ExecutionOutputCreate
from app.core.execution import ExecutionEngine
from sqlalchemy.orm import Session

# 全局变量，存储执行引擎实例
_execution_engine = None

def get_execution_engine() -> ExecutionEngine:
    """
    获取执行引擎实例
    
    Returns:
        ExecutionEngine: 执行引擎实例
    """
    global _execution_engine
    
    if _execution_engine is None:
        _execution_engine = ExecutionEngine()
    
    return _execution_engine

def execute_code(conversation_id: str, code: str, execution_id: Optional[str] = None, db: Session = None) -> Dict[str, Any]:
    """
    执行代码
    
    Args:
        conversation_id: 对话ID
        code: 要执行的代码
        execution_id: 执行ID，为None时自动生成
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 执行信息
    """
    if db is None:
        db = next(get_db())
    
    # 生成执行ID
    if execution_id is None:
        execution_id = f"exec_{uuid4().hex[:8]}"
    
    # 创建执行记录
    execution_data = ExecutionCreate(
        id=execution_id,
        conversation_id=conversation_id,
        code=code,
        status="pending",
        created_at=datetime.now()
    )
    
    # 保存到数据库
    execution = crud_execution.create(db, obj_in=execution_data)
    
    # 获取执行引擎
    engine = get_execution_engine()
    
    # 异步执行代码
    engine.execute_code(code, execution_id, conversation_id)
    
    return {
        "id": execution.id,
        "conversation_id": execution.conversation_id,
        "status": execution.status,
        "created_at": execution.created_at
    }

def cancel_execution(execution_id: str) -> bool:
    """
    取消执行
    
    Args:
        execution_id: 执行ID
        
    Returns:
        bool: 取消是否成功
    """
    # 获取执行引擎
    engine = get_execution_engine()
    
    # 取消执行
    return engine.cancel_execution(execution_id)

def get_execution(execution_id: str, db: Session = None) -> Optional[Dict[str, Any]]:
    """
    获取执行记录
    
    Args:
        execution_id: 执行ID
        db: 数据库会话
        
    Returns:
        Optional[Dict[str, Any]]: 执行记录信息
    """
    if db is None:
        db = next(get_db())
    
    # 获取执行记录
    execution = crud_execution.get(db, execution_id)
    if not execution:
        return None
    
    # 获取执行输出
    outputs = crud_execution.get_outputs(db, execution_id)
    
    # 构建响应
    return {
        "id": execution.id,
        "conversation_id": execution.conversation_id,
        "code": execution.code,
        "status": execution.status,
        "created_at": execution.created_at,
        "completed_at": execution.completed_at,
        "outputs": outputs
    }

def save_execution_output(execution_id: str, output_type: str, content: Any, db: Session = None) -> Dict[str, Any]:
    """
    保存执行输出
    
    Args:
        execution_id: 执行ID
        output_type: 输出类型 (stdout/stderr/result/error/figure)
        content: 输出内容
        db: 数据库会话
        
    Returns:
        Dict[str, Any]: 保存的输出信息
    """
    if db is None:
        db = next(get_db())
    
    # 检查执行记录是否存在
    execution = crud_execution.get(db, execution_id)
    if not execution:
        raise Exception(f"执行记录不存在: {execution_id}")
    
    # 创建输出记录
    output_data = ExecutionOutputCreate(
        execution_id=execution_id,
        output_type=output_type,
        content=content,
        timestamp=datetime.now()
    )
    
    # 保存到数据库
    output = crud_execution.create_output(db, obj_in=output_data)
    
    return {
        "id": output.id,
        "execution_id": output.execution_id,
        "output_type": output.output_type,
        "content": output.content,
        "timestamp": output.timestamp
    }

def update_execution_status(execution_id: str, status: str, db: Session = None) -> bool:
    """
    更新执行状态
    
    Args:
        execution_id: 执行ID
        status: 新状态 (pending/running/completed/error/cancelled)
        db: 数据库会话
        
    Returns:
        bool: 更新是否成功
    """
    if db is None:
        db = next(get_db())
    
    # 检查执行记录是否存在
    execution = crud_execution.get(db, execution_id)
    if not execution:
        return False
    
    # 更新状态
    update_data = {"status": status}
    
    # 如果状态为completed或error或cancelled，设置完成时间
    if status in ["completed", "error", "cancelled"]:
        update_data["completed_at"] = datetime.now()
    
    # 更新数据库
    crud_execution.update(db, db_obj=execution, obj_in=update_data)
    
    return True