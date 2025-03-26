from fastapi import APIRouter, Depends, HTTPException
from ..schemas.config import StatusResponse, SystemConfig,ModelStatusResponse
from ..services.model_service import get_model_status
from ..config import get_settings, save_config_to_file
from typing import Dict, Any
from app.utils.logger import get_logger
logger=get_logger(__name__)
# 创建路由实例
router = APIRouter()
class TagManager():
    def __init__(self):
        self.tag="aaaaaaaaaaaaaaaaa"
    def setTag(self,tag:str):
        self.tag=tag
        logger.info(f"tag被设置为了{tag}")
tagManager=TagManager()
@router.get("", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    settings = get_settings()
    model_status = await get_model_status()
    
    # 构建模型状态响应
    model_response = ModelStatusResponse(
        status="connected" if model_status["ok"] else "notconnected",
        type=settings.model.type
    )
    
    # 添加详细的模型状态到配置中
    config_dict = settings.model_dump()
    config_dict["model_status"] = model_status["models"]
    
    return StatusResponse(
        status="ok",
        version=settings.version,
        model=model_response,
        workspace=settings.workspace,
        config=config_dict,
        tag=tagManager.tag
    )


