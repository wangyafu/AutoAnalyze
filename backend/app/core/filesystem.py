import os
import time
import shutil
import threading
from typing import Dict, List, Any, Optional, Callable, Union
import pathlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.utils.logger import get_logger

logger = get_logger(__name__)

class FileSystemManager:
    """文件系统管理器，负责文件系统操作"""
    
    # 添加类变量来共享workspace
    _shared_workspace: Optional[str] = None
    
    def __init__(self):
        self.observer: Optional[Observer] = None
        self.watch_callbacks: List[Callable] = []
    
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
        
        # 如果已有监视器，停止它
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
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
    
    def watch_filesystem_changes(self, callback: Callable) -> bool:
        """监控文件系统变化
        
        Args:
            callback: 回调函数，接收变化事件作为参数
            
        Returns:
            bool: 是否成功启动监控
        """
        if not self.workspace:
            return False
        
        # 添加回调
        if callback not in self.watch_callbacks:
            self.watch_callbacks.append(callback)
        
        # 如果已有监视器，不需要再创建
        if self.observer:
            return True
        
        # 创建事件处理器
        class ChangeHandler(FileSystemEventHandler):
            def __init__(self, manager):
                self.manager = manager
            
            def on_any_event(self, event):
                # 忽略临时文件和隐藏文件
                if event.src_path.endswith("~") or "/" in event.src_path and "/" in event.src_path or "\\" in event.src_path and "\\" in event.src_path:
                    return
                
                # 创建事件对象
                event_data = {
                    "type": event.event_type,  # created, deleted, modified, moved
                    "path": os.path.relpath(event.src_path, self.manager.workspace),
                    "is_directory": event.is_directory,
                    "timestamp": time.time()
                }
                
                # 如果是移动事件，添加目标路径
                if hasattr(event, "dest_path") and event.dest_path:
                    event_data["dest_path"] = os.path.relpath(event.dest_path, self.manager.workspace)
                
                # 调用所有回调
                for cb in self.manager.watch_callbacks:
                    try:
                        cb(event_data)
                    except Exception as e:
                        logger.error(f"文件变化回调错误: {str(e)}")
        
        # 创建观察者
        self.observer = Observer()
        self.observer.schedule(ChangeHandler(self), self.workspace, recursive=True)
        self.observer.start()
        
        logger.info(f"启动文件系统监控: {self.workspace}")
        return True
    
    def stop_watching(self):
        """停止监控文件系统变化"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            logger.info("停止文件系统监控")

# 创建全局文件系统管理器实例
filesystem_manager = FileSystemManager()

if __name__ == "__main__":
    import asyncio
    import time
    
    def file_change_callback(event):
        """文件变化回调函数"""
        print(f"检测到文件变化: {event['type']} - {event['path']}")
    
    # 测试文件系统管理器
    def test_filesystem():
        # 设置工作目录为当前目录
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        current_dir="D://fakedata//exam_data"
        result = filesystem_manager.set_workspace(current_dir)
        print(f"\n1. 设置工作目录结果:")
        print(f"状态: {result['status']}")
        print(f"工作目录: {result.get('workspace')}")
        
        # 获取文件列表
        files = filesystem_manager.get_files()
        print(f"\n2. 获取文件列表:")
        print(f"状态: {files['status']}")
        print("文件列表:")
        for item in files['items']:
            type_str = "目录" if item['is_dir'] else "文件"
            print(f"- [{type_str}] {item['path']}")
        
        # 获取当前文件的预览
        current_file = os.path.basename(__file__)
        preview = filesystem_manager.get_file_preview(current_file)
        print(f"\n3. 获取文件预览 ({current_file}):")
        print(f"状态: {preview['status']}")
        print(f"文件大小: {preview.get('size', 0)} 字节")
        print(f"是否文本文件: {preview.get('is_text', False)}")
        if preview.get('content'):
            print("文件内容预览 (前100个字符):")
            print(preview['content'][:100] + "...")
        
        # 测试文件监控
        print("\n4. 测试文件系统监控:")
        filesystem_manager.watch_filesystem_changes(file_change_callback)
        print("开始监控文件系统变化...")
        print("将在5秒后停止监控...")
        
        # 等待5秒以观察文件系统变化
        time.sleep(5)
        
        # 停止监控
        filesystem_manager.stop_watching()
        print("停止文件系统监控")

    # 运行测试
    test_filesystem()