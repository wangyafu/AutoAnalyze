import os

from typing import Dict, List, Optional, Any, Union
import pandas as pd


from app.core.filesystem import FileSystemManager
import logging

logger = logging.getLogger(__name__)
# 获取文件系统管理器实例
fs_manager = FileSystemManager()
from app.core.agent.exec_code import exec_code
tools = [
    {
        "type": "function",
        "function": {
            "name": "read_directory",
            "description": "读取指定目录下的文件列表，返回文件名、类型、大小等信息。可用于浏览工作目录结构，了解可分析的数据文件。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "可选的子目录路径，相对于工作目录。不提供则列出根目录内容。"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_files",
            "description": "读取指定文件的内容。支持文本文件直接读取，CSV/Excel文件会自动生成数据预览，Word和PowerPoint文档会提取文本内容和结构信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "filenames": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "要读取的文件路径列表，相对于工作目录（例如：[\"data/sales.csv\", \"data/report.docx\"]）"
                    }
                },
                "required": ["filenames"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "exec_code",
            "description": "执行Python数据分析代码。支持pandas数据处理和matplotlib可视化，执行结果包含标准输出和生成的图表。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码。支持数据处理（pandas）和可视化（matplotlib）等常用数据分析库。"
                    }
                },
                "required": ["code"]
            }
        }
    }
]

async def read_directory(path: Optional[str] = None) -> Dict[str, Any]:
    """
    读取工作目录文件列表
    Tool Metadata:
    - name: read_directory
    - description: 读取指定目录下的文件列表，返回文件名、类型、大小等信息
    - parameters:
      - name: path
        type: string
        description: 可选子目录路径
        required: false
    """
    """读取工作目录下文件的基本信息
    
    Args:
        path: 可选的子目录路径，如果不提供则使用当前工作目录
        
    Returns:
        包含文件列表的字典
    """
    try:
        # 使用文件系统管理器获取文件列表
        files =  fs_manager.get_files(path)
        return {
            "status": "success",
            "files": files
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

async def read_file(filename: str) -> Dict[str, Any]:
    """
    读取文件内容
    Tool Metadata:
    - name: read_file
    - description: 读取指定文件内容，支持文本文件、CSV/Excel预览以及Word和PowerPoint文档
    - parameters:
      - name: filename
        type: string
        description: 文件路径
        required: true
    """
    """读取特定文件的内容
    
    Args:
        filename: 要读取的文件路径
        
    Returns:
        包含文件内容的字典
    """
    try:
        # 使用文件系统管理器处理文件
        return fs_manager.process_file(filename)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
async def read_files(filenames:list[str])->list[dict]:
    results=[]
    for name in filenames:
        result=await read_file(name)
        results.append(result)
    return results

class FunctionExecutor:
    def __init__(self,conversation_id:str):
        self.conversation_id=conversation_id

    async def execute(self, func_name: str, args: Dict) -> Any:
        """执行工具函数并返回结果"""
        if func_name == "read_directory":
            return await read_directory(args.get("path"))
        elif func_name == "read_files":
            return await read_files(args.get("filenames", []))
        elif func_name == "read_file":
            return await read_file(args["filename"])
        elif func_name == "exec_code":
            # 新增参数传递
            return await exec_code(args["code"], self.conversation_id)
        else:
            # 添加导入logger的语句，或者使用print替代
            
            logger.error(f"智能体调用了未知工具函数: {func_name}")
            raise ValueError(f"未知工具函数: {func_name}")
