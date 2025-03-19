import os
import time
import shutil
from typing import Dict, List, Any, Optional, Union
import pathlib

from app.utils.logger import get_logger

logger = get_logger(__name__)

class FileSystemManager:
    """文件系统管理器，负责文件系统操作"""
    
    # 添加类变量来共享workspace
    _shared_workspace: Optional[str] = None
    
    def __init__(self):
        pass
    
    @property
    def workspace(self) -> Optional[str]:
        """获取工作目录"""
        return self._shared_workspace
    
    @workspace.setter
    def workspace(self, value: Optional[str]):
        """设置工作目录"""
        self.__class__._shared_workspace = value
    
    def set_workspace(self, path: str) -> Dict[str, Any]:
        """设置工作目录
        
        Args:
            path: 工作目录路径
            
        Returns:
            Dict: 设置结果
        """
        # 验证路径
        if not os.path.exists(path):
            return {
                "status": "error",
                "error": "路径不存在"
            }
        
        if not os.path.isdir(path):
            return {
                "status": "error",
                "error": "路径不是目录"
            }
        
        # 设置工作目录
        self.workspace = os.path.abspath(path)
    
        logger.info(f"设置工作目录: {self.workspace}")
        
        return {
            "status": "success",
            "workspace": self.workspace
        }
    
    def get_files(self, path: Optional[str] = None) -> Dict[str, Any]:
        """获取文件列表
        
        Args:
            path: 相对于工作目录的路径，如果为None则获取工作目录
            
        Returns:
            Dict: 文件列表
        """
        if not self.workspace:
            return {
                "status": "error",
                "error": "工作目录未设置"
            }
        
        # 确定目标路径
        target_path = self.workspace
        if path:
            # 确保路径是相对于工作目录的
            target_path = os.path.normpath(os.path.join(self.workspace, path))
            
            # 安全检查：确保目标路径在工作目录内
            if not target_path.startswith(self.workspace):
                return {
                    "status": "error",
                    "error": "路径超出工作目录范围"
                }
        
        # 检查路径是否存在
        if not os.path.exists(target_path):
            return {
                "status": "error",
                "error": "路径不存在"
            }
        
        # 检查路径是否是目录
        if not os.path.isdir(target_path):
            return {
                "status": "error",
                "error": "路径不是目录"
            }
        
        # 获取文件列表
        items = []
        for item in os.listdir(target_path):
            item_path = os.path.join(target_path, item)
            is_dir = os.path.isdir(item_path)
            
            # 获取文件大小和修改时间
            stats = os.stat(item_path)
            size = stats.st_size if not is_dir else None
            modified = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_mtime))  # 转换为ISO 8601格式
            
            # 创建文件项
            file_item = {
                "name": item,
                "path": os.path.relpath(item_path, self.workspace),
                "is_dir": is_dir,
                "size": size,
                "modified": modified  # 修改后的时间格式示例：2023-12-31T14:30:00
            }
            
            items.append(file_item)
        
        # 按类型和名称排序：目录在前，文件在后
        items.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        
        return {
            "status": "success",
            "path": os.path.relpath(target_path, self.workspace) if target_path != self.workspace else "",
            "items": items
        }
    def get_files_info(self, paths: List[str]) -> Dict[str, Any]:
        """批量获取多个文件的详细信息
        
        Args:
            paths: 相对于工作目录的文件路径列表
                
        Returns:
            Dict: 包含多个文件信息的字典
        """
        if not self.workspace:
            return {
                "status": "error",
                "error": "工作目录未设置"
            }
        
        results = {}
        for path in paths:
            # 确定目标路径
            target_path = os.path.normpath(os.path.join(self.workspace, path))
            
            # 安全检查：确保目标路径在工作目录内
            if not target_path.startswith(self.workspace):
                results[path] = {
                    "status": "error",
                    "error": "路径超出工作目录范围"
                }
                continue
            
            # 检查文件是否存在
            if not os.path.exists(target_path):
                results[path] = {
                    "status": "error",
                    "error": "文件不存在"
                }
                continue
            
            # 获取文件信息
            stats = os.stat(target_path)
            is_dir = os.path.isdir(target_path)
            
            # 转换时间格式
            modified = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_mtime))
            created = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_ctime))
            
            file_info = {
                "status": "success",
                "path": path,
                "name": os.path.basename(path),
                "is_dir": is_dir,
                "size": stats.st_size if not is_dir else None,
                "modified": modified,  # 修改后的时间格式
                "created": created     # 新增创建时间字段
            }
            
            # 如果是文件，尝试获取内容预览
            if not is_dir:
                file_ext = os.path.splitext(target_path)[1].lower()
                is_text = file_ext in [".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".csv", ".xml", ".yml", ".yaml", ".ini", ".cfg", ".conf"]
                file_info["is_text"] = is_text
                
                # 对于文本文件，尝试读取内容
                if is_text and stats.st_size <= 1024 * 1024:  # 限制为1MB
                    try:
                        with open(target_path, "r", encoding="utf-8") as f:
                            file_info["content"] = f.read()
                    except UnicodeDecodeError:
                        file_info["is_text"] = False
                    except Exception as e:
                        file_info["read_error"] = str(e)
            
            results[path] = file_info
        
        return {
            "status": "success",
            "files": results
        }
    def get_file_preview(self, path: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """获取文件预览
        
        Args:
            path: 相对于工作目录的文件路径
            max_size: 最大预览大小（字节）
            
        Returns:
            Dict: 文件预览
        """
        if not self.workspace:
            return {
                "status": "error",
                "error": "工作目录未设置"
            }
        
        # 确定目标路径
        target_path = os.path.normpath(os.path.join(self.workspace, path))
        
        # 安全检查：确保目标路径在工作目录内
        if not target_path.startswith(self.workspace):
            return {
                "status": "error",
                "error": "路径超出工作目录范围"
            }
        
        # 检查文件是否存在
        if not os.path.exists(target_path):
            return {
                "status": "error",
                "error": "文件不存在"
            }
        
        # 检查是否是文件
        if not os.path.isfile(target_path):
            return {
                "status": "error",
                "error": "路径不是文件"
            }
        
        # 获取文件大小
        file_size = os.path.getsize(target_path)
        
        # 判断文件类型
        file_ext = os.path.splitext(target_path)[1].lower()
        is_text = file_ext in [".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".csv", ".xml", ".yml", ".yaml", ".ini", ".cfg", ".conf"]
        
        # 如果文件太大或不是文本文件，返回基本信息
        if file_size > max_size or not is_text:
            return {
                "status": "success",
                "path": path,
                "size": file_size,
                "is_text": is_text,
                "content": None,
                "truncated": True
            }
        
        # 读取文件内容
        try:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read(max_size)
                truncated = file_size > max_size
            
            return {
                "status": "success",
                "path": path,
                "size": file_size,
                "is_text": True,
                "content": content,
                "truncated": truncated
            }
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码或返回二进制文件信息
            return {
                "status": "success",
                "path": path,
                "size": file_size,
                "is_text": False,
                "content": None,
                "truncated": True
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"读取文件失败: {str(e)}"
            }
    
    def get_file_content(self, path: str) -> Dict[str, Any]:
        """获取文件内容
        
        Args:
            path: 相对于工作目录的文件路径
            
        Returns:
            Dict: 文件内容
        """
        # 不限制大小的文件预览
        return self.get_file_preview(path, max_size=50 * 1024 * 1024)  # 50MB上限

# 创建全局文件系统管理器实例
filesystem_manager = FileSystemManager()