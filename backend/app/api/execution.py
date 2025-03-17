from fastapi import APIRouter, Depends, HTTPException, Path
from app.schemas.execution import ExecutionRequest, ExecutionResponse, ExecutionStatusResponse, CancelExecutionRequest
from app.services.execution_service import execute_code, cancel_execution, get_execution
from typing import Dict, Any
import uuid

# 创建路由实例
router = APIRouter()


@router.post("", response_model=ExecutionResponse)
async def execute_code_request(request: ExecutionRequest):
    """执行代码"""
    try:
        # 生成执行ID
        execution_id = str(uuid.uuid4())
        
        # 执行代码（异步启动）
        execution = execute_code(
            conversation_id=request.conversation_id,
            code=request.code,
            execution_id=execution_id
        )
        
        return execution
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{execution_id}/cancel", response_model=Dict[str, Any])
async def cancel_code_execution(execution_id: str = Path(..., description="执行ID")):
    """中止代码执行"""
    try:
        success = cancel_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="执行任务不存在或已完成")
        
        return {"status": "success", "message": "执行已取消"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{execution_id}", response_model=ExecutionStatusResponse)
async def get_execution_status(execution_id: str = Path(..., description="执行ID")):
    """获取执行状态"""
    try:
        execution = get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="执行任务不存在")
        
        return execution
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))