from fastapi import APIRouter, Depends, HTTPException, Path
from app.schemas.execution import ExecutionRequest, ExecutionResponse, ExecutionStatusResponse, CancelExecutionRequest
from app.services.execution_service import execute_code, cancel_execution, get_execution
from typing import Dict, Any
import uuid

# 创建路由实例
router = APIRouter()

