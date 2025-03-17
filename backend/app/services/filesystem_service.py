import os
import shutil
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from ..config import get_settings
from ..schemas.filesystem import FileItem, DirectoryItem, FilePreview, FileSystemItem
from ..utils.file_utils import get_file_type, is_text_file, format_file_size

# 全局变量，存储当前工作目录
_workspace = None

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
    global _workspace
    
    # 验证目录是否存在
    if not os.path.exists(path):
        raise Exception(f"目录不存在: {path}")
    
    # 验证是否为目录
    if not os.path.isdir(path):
        raise Exception(f"路径不是目录: {path}")
    
    # 验证是否有读写权限
    if not os.access(path, os.R_OK | os.W_OK):
        raise Exception(f"目录无读写权限: {path}")
    
    # 设置工作目录
    _workspace = path
    
    # 更新配置
    settings = get_settings()
    settings.workspace = path
    
    return _workspace

def get_workspace() -> str:
    """
    获取当前工作目录
    
    Returns:
        str: 当前工作目录路径
        
    Raises:
        Exception: 工作目录未设置时抛出异常
    """
    if _workspace is None:
        raise Exception("工作目录未设置")
    
    return _workspace

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
    获取文件目录结构
    
    Args:
        path: 相对于工作目录的路径，为None时返回工作目录下的文件
        
    Returns:
        List[FileSystemItem]: 文件系统项目列表
        
    Raises:
        Exception: 路径不存在或无法访问时抛出异常
    """
    # 获取绝对路径
    abs_path = get_absolute_path(path)
    
    # 验证路径是否存在
    if not os.path.exists(abs_path):
        raise Exception(f"路径不存在: {path}")
    
    # 验证是否为目录
    if not os.path.isdir(abs_path):
        raise Exception(f"路径不是目录: {path}")
    
    # 获取目录内容
    items = []
    for item in os.listdir(abs_path):
        item_path = os.path.join(abs_path, item)
        rel_path = os.path.relpath(item_path, get_workspace())
        
        if os.path.isdir(item_path):
            # 目录
            dir_items_count = len(os.listdir(item_path))
            items.append(DirectoryItem(
                name=item,
                path=rel_path,
                items_count=dir_items_count
            ))
        else:
            # 文件
            file_size = os.path.getsize(item_path)
            file_type = get_file_type(item_path)
            last_modified = os.path.getmtime(item_path)
            extension = os.path.splitext(item)[1].lstrip('.')
            
            items.append(FileItem(
                name=item,
                path=rel_path,
                size=file_size,
                formatted_size=format_file_size(file_size),
                type=file_type,
                last_modified=last_modified,
                extension=extension
            ))
    
    # 排序：目录在前，文件在后，按名称排序
    items.sort(key=lambda x: (not isinstance(x, DirectoryItem), x.name.lower()))
    
    return items

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
    extension = os.path.splitext(file_name)[1].lstrip('.')
    
    # 判断是否为文本文件
    is_text = is_text_file(abs_path)
    
    # 预览内容
    preview_content = ""
    truncated = False
    
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
    else:
        # 二进制文件，不提供预览内容
        preview_content = "[二进制文件，无法预览]"
    
    # 构建预览响应
    return FilePreview(
        name=file_name,
        path=path,
        type=file_type,
        size=file_size,
        formatted_size=format_file_size(file_size),
        preview=preview_content,
        truncated=truncated,
        extension=extension
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

def start_file_watcher():
    """
    启动文件监视器，监控工作目录的文件变化
    
    Returns:
        None
    """
    # 此功能需要实现文件系统监控
    # 可以使用watchdog库实现
    pass