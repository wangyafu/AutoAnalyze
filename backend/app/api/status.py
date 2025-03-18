from fastapi import APIRouter, Depends, HTTPException
from ..schemas.config import StatusResponse, SystemConfig,ModelStatusResponse
from ..services.model_service import get_model_status
from ..config import get_settings, save_config_to_file
from typing import Dict, Any

# 创建路由实例
router = APIRouter()


@router.get("", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    settings = get_settings()
    model_status = await get_model_status()
    
    return StatusResponse(
        status="ok",
        version=settings.version,
        model=ModelStatusResponse(status="connected" if model_status["status"] else "notconnected",type=settings.model.type),
        workspace=settings.workspace,
        config=settings.model_dump()
    )


