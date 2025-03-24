import os
import shutil
import time
import asyncio
from typing import List, Optional, Dict, Any, Union, Callable
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.config import get_settings
from app.schemas.filesystem import FileItem, DirectoryItem, FilePreview, FileSystemItem
from app.utils.file_utils import get_file_type, is_text_file, format_file_size
from app.core.filesystem import filesystem_manager
from app.websocket.manager import manager
from datetime import datetime
from app.utils.logger import get_logger
import csv
import io
import pandas as pd
logger = get_logger(__name__)

def set_workspace(path: str) -> str:
    """
    设置工作目录
    
    Args:
        path: 工作目录路径
        
    Returns:
        str: 设置后的工作目录路径
    
    Raises:
        Exception: 目录不存在或无法访问时抛出异常
    """
    result = filesystem_manager.set_workspace(path)
    if result["status"] == "error":
        raise Exception(result["error"])
    
    # 更新配置
    settings = get_settings()
    settings.workspace = path
    
    return result["workspace"]

def get_workspace() -> str:
    """
    获取当前工作目录
    
    Returns:
        str: 当前工作目录路径
        
    Raises:
        Exception: 工作目录未设置时抛出异常
    """
    workspace = filesystem_manager.workspace
    if workspace is None:
        raise Exception("工作目录未设置")
    
    return workspace

def get_absolute_path(relative_path: Optional[str] = None) -> str:
    """
    获取相对于工作目录的绝对路径
    
    Args:
        relative_path: 相对路径，为None时返回工作目录
        
    Returns:
        str: 绝对路径
        
    Raises:
        Exception: 工作目录未设置或路径超出工作目录范围时抛出异常
    """
    workspace = get_workspace()
    
    if relative_path is None or relative_path == "":
        return workspace
    
    # 构建绝对路径
    abs_path = os.path.normpath(os.path.join(workspace, relative_path))
    
    # 验证路径是否在工作目录内
    if not abs_path.startswith(workspace):
        raise Exception(f"路径超出工作目录范围: {relative_path}")
    
    return abs_path

def get_files(path: Optional[str] = None) -> List[FileSystemItem]:
    """
    获取文件目录结构，递归获取子目录内容
    
    Args:
        path: 相对于工作目录的路径，为None时返回工作目录下的文件
        
    Returns:
        List[FileSystemItem]: 文件系统项目列表
        
    Raises:
        Exception: 路径不存在或无法访问时抛出异常
    """
    def _list_directory(current_path: str) -> List[FileSystemItem]:
        items = []
        try:
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                rel_path = os.path.relpath(item_path, get_workspace())
                last_modified = os.path.getmtime(item_path)
                
                if os.path.isdir(item_path):
                    # 递归获取子目录内容
                    children = _list_directory(item_path)
                    items.append(FileSystemItem(root=DirectoryItem(
                        name=item,
                        path=rel_path,
                        type="directory",
                        modified=datetime.fromtimestamp(last_modified),
                        children=children  # 添加子目录内容
                    )))
                else:
                    file_size = os.path.getsize(item_path)
                    extension = os.path.splitext(item)[1].lstrip('.')
                    
                    items.append(FileSystemItem(root=FileItem(
                        name=item,
                        path=rel_path,
                        type="file",
                        size=file_size,
                        modified=datetime.fromtimestamp(last_modified),
                        extension=extension
                    )))
            
            # 排序：目录在前，文件在后，按名称排序
            items.sort(key=lambda x: (not isinstance(x.root, DirectoryItem), x.root.name.lower()))
            return items
            
        except Exception as e:
            logger.error(f"读取目录失败 {current_path}: {str(e)}")
            return []

    # 获取绝对路径
    abs_path = get_absolute_path(path)
    
    # 验证路径是否存在
    if not os.path.exists(abs_path):
        raise Exception(f"路径不存在: {path}")
    
    # 验证是否为目录
    if not os.path.isdir(abs_path):
        raise Exception(f"路径不是目录: {path}")
    result=_list_directory(abs_path)
    # 递归获取目录内容
    return result

def get_file_preview(path: str, max_size: int = 100000) -> FilePreview:
    """
    获取文件内容预览
    
    Args:
        path: 相对于工作目录的文件路径
        max_size: 最大预览大小（字节）
        
    Returns:
        FilePreview: 文件预览信息
        
    Raises:
        Exception: 文件不存在或无法访问时抛出异常
    """
    # 获取绝对路径
    abs_path = get_absolute_path(path)
    
    # 验证文件是否存在
    if not os.path.exists(abs_path):
        raise Exception(f"文件不存在: {path}")
    
    # 验证是否为文件
    if not os.path.isfile(abs_path):
        raise Exception(f"路径不是文件: {path}")
    
    # 获取文件信息
    file_size = os.path.getsize(abs_path)
    file_name = os.path.basename(abs_path)
    file_type = get_file_type(abs_path)
    extension = os.path.splitext(file_name)[1].lower().lstrip('.')
    
    # 判断是否为文本文件
    is_text = is_text_file(abs_path)
    
    # 预览内容和类型
    preview_content = ""
    truncated = False
    preview_type = "text"  # 默认为文本预览
    base64_data = None
    structured_data = None
    
    # 根据文件类型处理预览
    if is_text:
        # 文本文件，读取内容
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                if file_size > max_size:
                    preview_content = f.read(max_size)
                    truncated = True
                else:
                    preview_content = f.read()
        except Exception as e:
            raise Exception(f"读取文件失败: {str(e)}")
    elif file_type == "image":
        # 图片文件，转换为Base64
        preview_type = "image"
        try:
            import base64
            # 限制图片大小
            if file_size > 5 * 1024 * 1024:  # 5MB限制
                preview_content = "[图片文件过大，无法预览]"
                truncated = True
            else:
                with open(abs_path, 'rb') as f:
                    image_data = f.read()
                    base64_data = base64.b64encode(image_data).decode('utf-8')
                    preview_content = "[图片文件]"
        except Exception as e:
            preview_content = f"[图片文件读取失败: {str(e)}]"
    elif extension in ["csv", "xls", "xlsx"]:
        # 表格文件，解析为结构化数据
        preview_type = "excel" if extension in ["xls", "xlsx"] else "csv"
        try:
            if extension == "csv":
                
                # 读取CSV文件
                with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                    csv_reader = csv.reader(f)
                    rows = list(csv_reader)
                    if rows:
                        headers = rows[0]
                        data = rows[1:100]  # 限制行数
                        structured_data = {
                            "columns": headers,
                            "data": data
                        }
                        preview_content = "[CSV表格数据]"
                    else:
                        preview_content = "[空CSV文件]"
            elif extension in ["xls", "xlsx"]:
                try:
                    logger.info(f"尝试读取{abs_path}")
                    # 读取Excel文件
                    df = pd.read_excel(abs_path, nrows=100)  # 限制行数
                    structured_data = {
                        "columns": df.columns.tolist(),
                        "data": df.values.tolist()
                    }
                    preview_content = "[Excel表格数据]"
                except ImportError as e:
                    preview_content = f"[Pandas读取Excel文件出现错误:{e}]"
                    raise e
        except Exception as e:
            preview_content = f"[表格文件读取失败: {str(e)}]"
    else:
        # 其他二进制文件，不提供预览内容
        preview_content = "[二进制文件，无法预览]"
    
    # 构建预览响应
    return FilePreview(
        name=file_name,
        path=path,
        type=file_type,
        size=file_size,
        content=preview_content,
        is_binary=not is_text,
        is_truncated=truncated,
        encoding="utf-8" if is_text else None,
        preview_type=preview_type,
        base64_data=base64_data,
        structured_data=structured_data
    )

def get_file_content(path: str) -> str:
    """
    获取文件完整内容
    
    Args:
        path: 相对于工作目录的文件路径
        
    Returns:
        str: 文件内容
        
    Raises:
        Exception: 文件不存在、不是文本文件或无法访问时抛出异常
    """
    # 获取绝对路径
    abs_path = get_absolute_path(path)
    
    # 验证文件是否存在
    if not os.path.exists(abs_path):
        raise Exception(f"文件不存在: {path}")
    
    # 验证是否为文件
    if not os.path.isfile(abs_path):
        raise Exception(f"路径不是文件: {path}")
    
    # 判断是否为文本文件
    if not is_text_file(abs_path):
        raise Exception(f"不是文本文件: {path}")
    
    # 读取文件内容
    try:
        with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"读取文件失败: {str(e)}")




if __name__ == "__main__":
# 测试文件系统服务
    def test_filesystem_service():
        try:
            # 1. 测试设置工作目录
            test_dir = ""  # 请确保此目录存在
            print(filesystem_manager.set_workspace(test_dir))
            print(get_file_preview("你好.xlsx"))
        except Exception as e:
            print(e)


# 运行测试
    test_filesystem_service()