from fastapi import APIRouter
from . import status, workspace, conversations, execution

# 创建API路由实例
api_router = APIRouter()

# 注册状态API路由
api_router.include_router(status.router, prefix="/status", tags=["status"])

# 注册工作区API路由
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(workspace.files_router, prefix="/files", tags=["files"])

# 注册对话API路由
api_router.include_router(conversations.router, prefix="/conversations", tags=["conversations"])

# 注册执行API路由
api_router.include_router(execution.router, prefix="/execute", tags=["execution"])