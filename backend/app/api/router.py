from fastapi import APIRouter
from . import status, workspace, conversations
from fastapi import APIRouter, Depends, HTTPException
from ..schemas.config import StatusResponse, SystemConfig
from ..services.model_service import get_model_status
from ..config import get_settings, save_config_to_file,reset_settings
from app.api.status import get_status
# 创建API路由实例
api_router = APIRouter()

# 注册状态API路由
api_router.include_router(status.router, prefix="/status", tags=["status"])

# 注册工作区API路由
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(workspace.files_router, prefix="/files", tags=["files"])

# 注册对话API路由
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])



@api_router.put("/config", response_model=StatusResponse)
async def update_config(config: SystemConfig):
    """更新系统配置"""
    settings = get_settings()

    # 更新模型配置
    if config.model:
        # 只更新非空值
        model_data = config.model.model_dump(exclude_unset=True)
        if model_data:
            for key, value in model_data.items():
                if value is not None:  # 跳过空值
                    setattr(settings.model, key, value)

    # 保存配置到文件
    try:
        save_config_to_file(settings, settings.config_path)
        # 重置配置缓存，确保下次获取是更新后的配置
        reset_settings()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")

    return await get_status()