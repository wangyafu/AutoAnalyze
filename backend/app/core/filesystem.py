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

    

    def get_file_info(self, path: str, preview_chars: int = 5000) -> Dict[str, Any]:
        """获取文件内容和基本信息

        Args:
            path: 相对于工作目录的文件路径
            preview_chars: 预览的字符数量

        Returns:
            Dict: 文件内容和信息
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

        try:
            # 获取文件基本信息
            stats = os.stat(target_path)
            file_size = stats.st_size
            modified = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(stats.st_mtime))

            # 读取文件内容
            try:
                with open(target_path, "r", encoding="utf-8") as f:
                    content = f.read(preview_chars)
                    is_truncated = len(content) < file_size
                    
                return {
                    "status": "success",
                    "size": file_size,
                    "modified": modified,
                    "content": content,
                    "truncated": is_truncated
                }
            except UnicodeDecodeError:
                # 如果不是文本文件，返回基本信息
                return {
                    "status": "success",
                    "size": file_size,
                    "modified": modified,
                    "content": None,
                    "is_binary": True
                }
        except Exception as e:
            return {
                "status": "error",
                "error": f"读取文件失败: {str(e)}"
            }
    def process_file(self, filename: str) -> Dict[str, Any]:
        """根据文件类型处理文件并返回相应的内容和预览信息
        
        Args:
            filename: 要处理的文件路径
            
        Returns:
            包含文件内容和预览信息的字典
        """
        try:
            info = self.get_file_info(filename)
            file_type = os.path.splitext(filename)[1].lower()[1:]
            
            result = {
                "status": "success",
                "info": info
            }
            target_path = os.path.normpath(os.path.join(self.workspace, filename))
            # 根据文件类型进行不同处理
            if file_type in ['csv', 'xlsx', 'xls']:
                preview = self._process_tabular_file(target_path, file_type)
                result["info"].pop("content")
                result["info"].pop("truncated")
                if preview["ok"]:
                    result["preview"] = preview
                    
            elif file_type in ['docx', 'doc']:
                preview = self._process_word_document(target_path)
                result["info"].pop("content")
                result["info"].pop("truncated")
                if preview["ok"]:
                    result["preview"] = preview
                    
            elif file_type in ['pptx', 'ppt']:
                preview = self._process_powerpoint(target_path)
                result["info"].pop("content")
                result["info"].pop("truncated")
                if preview["ok"]:
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
            # 尝试不同的编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'iso-8859-1']
            df = None
            used_encoding = None
            
            if file_type == 'csv':
                for encoding in encodings:
                    try:
                        df = pd.read_csv(absolute_path, nrows=20, encoding=encoding)
                        # 计算总行数
                        with open(absolute_path, 'r', encoding=encoding) as f:
                            total_rows = sum(1 for _ in f)
                        used_encoding = encoding
                        break
                    except (UnicodeDecodeError, pd.errors.ParserError):
                        continue
                
                if df is None:
                    raise Exception("无法使用支持的编码读取文件")
            else:
                # Excel文件不需要处理编码
                df = pd.read_excel(absolute_path, nrows=20)
                # 读取总行数
                full_df = pd.read_excel(absolute_path)
                total_rows = len(full_df)
                used_encoding = 'binary'  # Excel是二进制格式
            
           
            
            return {
                "shape": (total_rows, len(df.columns)),  # 显示实际总行数
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.astype(str).to_dict(),
                "head": df.head().to_dict(orient='records'),
                "tail": df.tail().to_dict(orient='records'),
                "total_rows": total_rows,      # 新增字段，显示实际总行数
                "encoding": used_encoding, # 新增字段，显示使用的编码
                "ok":True
            }
        except Exception as e:
            logger.error(f"处理表格文件失败: {str(e)}")
            return {
                "ok":False,
                "error": str(e)
            }
    
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
            logger.error(f"处理Word文档失败: {str(e)}")
            return {
                "ok":False,
                "error": str(e)
            }
    
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
            logger.error(f"处理PPT文件失败: {str(e)}")
            return {
                "ok":False,
                "error": str(e)
            }
    
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

if __name__ == "__main__":
    # 设置测试工作目录
    test_dir =""
    result = filesystem_manager.set_workspace(test_dir)
    print(f"设置工作目录: {result}")
    
    # 测试不同类型的文件
    test_files = [
        
        "销售数据.csv",          # CSV文件
        
    ]
    
    for file in test_files:
        print(f"\n处理文件: {file}")
        try:
            result = filesystem_manager.process_file(file)
            print(result)

        except Exception as e:
            print(f"测试异常: {str(e)}")


