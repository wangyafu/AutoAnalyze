from fastapi import APIRouter, Depends, HTTPException
from ..schemas.config import StatusResponse, SystemConfig
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
        model_status=model_status,
        workspace=settings.workspace,
        config=settings.dict()
    )


@router.put("/config", response_model=StatusResponse)
async def update_config(config: SystemConfig):
    """更新系统配置"""
    settings = get_settings()
    
    # 更新配置
    for key, value in config.dict().items():
        if hasattr(settings, key):
            setattr(settings, key, value)
    
    # 保存配置到文件
    try:
        save_config_to_file(settings, settings.config_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
    
    return await get_status()