from fastapi import APIRouter, Depends, HTTPException, Query
from app.schemas.filesystem import WorkspaceRequest, WorkspaceResponse, FileItem, DirectoryItem, FilePreview, FileSystemItem
from app.core.filesystem import filesystem_manager  # 导入 filesystem_manager 实例
from app.services.filesystem_service import get_files, get_file_preview, get_workspace
from typing import List, Optional, Union
import os
from app.utils.logger import get_logger
# 创建工作区路由实例
router = APIRouter()

# 创建文件路由实例
files_router = APIRouter()
logger = get_logger(__name__)

@router.post("", response_model=WorkspaceResponse)
async def set_workspace_path(request: WorkspaceRequest):
    logger.info(f"前端选择工作目录为: {request.path}")
    """设置工作目录"""
    try:
        result = filesystem_manager.set_workspace(request.path)

        if result["status"] == "error":
            return WorkspaceResponse(
                status="error",
                error=result["error"]
            )
        

        return WorkspaceResponse(
            status="success",
            workspace=result["workspace"]
        )
    except Exception as e:
        return WorkspaceResponse(
            status="error",
            error=str(e)
        )


@router.get("", response_model=WorkspaceResponse)
async def get_workspace_path():
    """获取当前工作目录"""
    try:
        workspace = get_workspace()
        return WorkspaceResponse(
            status="success",
            workspace=workspace
        )
    except Exception as e:
        return WorkspaceResponse(
            status="error",
            error=str(e)
        )


@files_router.get("", response_model=List[FileSystemItem])
async def get_file_structure(path: Optional[str] = Query(None, description="相对于工作目录的路径")):
    """获取文件目录结构"""
    try:
        files = get_files(path)
        return files
    except Exception as e:
        logger.error(f"获取文件目录结构失败: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@files_router.get("/preview", response_model=FilePreview)
async def preview_file(path: str = Query(..., description="相对于工作目录的文件路径"),
                      max_size: int = Query(100000, description="最大预览大小（字节）")):
    """获取文件内容预览"""
    try:
        preview = get_file_preview(path, max_size)
        return preview
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))