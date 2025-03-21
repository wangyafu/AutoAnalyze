import os
import pandas as pd
from typing import Dict, List, Any, Optional
from markitdown import MarkItDown
from app.utils.logger import get_logger
logger=get_logger(__name__)
import time
class FileSystemManager:
    # 添加类变量来共享workspace
    _shared_workspace: Optional[str] = None



    def __init__(self):
        self.base_dir = os.getcwd()
        self.md = MarkItDown()

        # 添加类变量来共享workspace




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
        is_text = file_ext in [".txt", ".py", ".js", ".html", ".css", ".json", ".md", ".csv", ".xml", ".yml", ".yaml",
                               ".ini", ".cfg", ".conf"]

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
    def process_file(self, filename: str) -> Dict[str, Any]:
        """根据文件类型处理文件并返回相应的内容和预览信息
        
        Args:
            filename: 要处理的文件路径
            
        Returns:
            包含文件内容和预览信息的字典
        """
        try:
            content = self.get_file_content(filename)
            file_type = os.path.splitext(filename)[1].lower()[1:]
            
            result = {
                "status": "success",
                "content": content
            }
            target_path = os.path.normpath(os.path.join(self.workspace, filename))
            # 根据文件类型进行不同处理
            if file_type in ['csv', 'xlsx', 'xls']:
                preview = self._process_tabular_file(target_path, file_type)
                if preview:
                    result["preview"] = preview
            
            elif file_type in ['docx', 'doc']:
                preview = self._process_word_document(target_path)
                if preview:
                    result["preview"] = preview
            
            elif file_type in ['pptx', 'ppt']:
                preview = self._process_powerpoint(target_path)
                if preview:
                    result["preview"] = preview
                    
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _process_tabular_file(self, absolute_path: str, file_type: str) -> Optional[Dict[str, Any]]:
        """处理表格类文件（CSV、Excel）
        
        Args:
            absolute_path: 文件路径
            file_type: 文件类型
            
        Returns:
            表格预览信息
        """
        try:
            if file_type == 'csv':
                df = pd.read_csv(absolute_path)
            else:
                df = pd.read_excel(absolute_path)
            
            return {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "head": df.head().to_dict(orient='records')
            }
        except Exception:
            return None
    
    def _process_word_document(self, absolute_path: str) -> Optional[Dict[str, Any]]:
        """处理Word文档
        
        Args:
            absolute_path: 文件路径
            
        Returns:
            Word文档预览信息
        """
        try:
            # 使用markitdown处理Word文档
            result = self.md.convert(absolute_path)
            
            # 提取文档结构和内容摘要
            return {
                "text_content": result.text_content[:1000] + "..." if len(result.text_content) > 1000 else result.text_content,
                "metadata": {
                    "title": os.path.basename(absolute_path),
                    "pages": getattr(result, "pages", "未知"),
                    "word_count": len(result.text_content.split()),
                    "has_images": hasattr(result, "images") and len(getattr(result, "images", [])) > 0
                },
                "structure": self._extract_document_structure(result.text_content)
            }
        except Exception:
            return None
    
    def _process_powerpoint(self, absolute_path: str) -> Optional[Dict[str, Any]]:
        """处理PowerPoint演示文稿
        
        Args:
            absolute_path: 文件路径
            
        Returns:
            PowerPoint预览信息
        """
        try:
            # 使用markitdown处理PPT文档
            result = self.md.convert(absolute_path)
            
            # 提取演示文稿结构和内容摘要
            return {
                "text_content": result.text_content[:1000] + "..." if len(result.text_content) > 1000 else result.text_content,
                "metadata": {
                    "title": os.path.basename(absolute_path),
                    "slides": getattr(result, "slides", "未知"),
                    "has_images": hasattr(result, "images") and len(getattr(result, "images", [])) > 0
                },
                "structure": self._extract_presentation_structure(result.text_content)
            }
        except Exception:
            return None
    
    def _extract_document_structure(self, text_content: str) -> List[str]:
        """从文档内容中提取结构（标题等）
        
        Args:
            text_content: 文档文本内容
            
        Returns:
            文档结构列表
        """
        # 简单实现：尝试提取可能的标题行
        lines = text_content.split('\n')
        potential_headings = []
        
        for line in lines:
            line = line.strip()
            # 简单的启发式方法：短行且不以标点结尾的可能是标题
            if line and len(line) < 100 and line[-1] not in '.,:;?!':
                potential_headings.append(line)
                if len(potential_headings) >= 10:  # 最多返回10个可能的标题
                    break
                    
        return potential_headings
    
    def _extract_presentation_structure(self, text_content: str) -> List[str]:
        """从演示文稿内容中提取结构（幻灯片标题等）
        
        Args:
            text_content: 演示文稿文本内容
            
        Returns:
            演示文稿结构列表
        """
        # 与文档结构提取类似，但针对PPT的特点进行调整
        return self._extract_document_structure(text_content)  # 简单实现可以复用
filesystem_manager = FileSystemManager()

