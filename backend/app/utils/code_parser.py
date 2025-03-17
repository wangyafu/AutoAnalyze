"""
代码解析工具模块

提供从消息内容中解析代码块、提取代码语言等功能
"""
import re
from typing import List, Tuple, Optional, Dict

# 支持的语言映射
LANGUAGE_ALIASES: Dict[str, str] = {
    "python": "python",
    "py": "python",
    "javascript": "javascript",
    "js": "javascript",
    "typescript": "typescript",
    "ts": "typescript",
    "html": "html",
    "css": "css",
    "json": "json",
    "sql": "sql",
    "bash": "bash",
    "shell": "bash",
    "sh": "bash",
    "r": "r",
    "cpp": "cpp",
    "c++": "cpp",
    "c": "c",
    "java": "java",
    "rust": "rust",
    "go": "go",
    "ruby": "ruby",
    "php": "php",
    "csharp": "csharp",
    "c#": "csharp",
    "plaintext": "plaintext",
    "text": "plaintext",
}

def parse_code(content: str) -> List[Tuple[str, str]]:
    """
    从消息内容中解析代码块
    
    Args:
        content: 消息内容
        
    Returns:
        List[Tuple[str, str]]: 代码块列表，每个元素为 (语言, 代码内容) 的元组
    """
    # 匹配 Markdown 代码块: ```language\ncode\n```
    pattern = r"```([\w+#.]*)\n([\s\S]*?)```"
    matches = re.findall(pattern, content)
    
    # 处理匹配结果
    code_blocks = []
    for language, code in matches:
        # 规范化语言标识
        normalized_language = extract_language(language)
        code_blocks.append((normalized_language, code.strip()))
    
    return code_blocks

def extract_language(code_block_header: str) -> str:
    """
    提取代码语言
    
    Args:
        code_block_header: 代码块语言标识部分
        
    Returns:
        str: 规范化的语言标识，如果无法识别则返回 "plaintext"
    """
    # 移除可能的文件路径或其他标记
    language = code_block_header.strip().lower().split(':')[0].split('(')[0]
    
    # 查找语言别名映射
    return LANGUAGE_ALIASES.get(language, "plaintext")

def extract_code_from_message(message: Dict) -> Optional[Tuple[str, str]]:
    """
    从消息对象中提取第一个代码块
    
    Args:
        message: 消息对象，包含 content 字段
        
    Returns:
        Optional[Tuple[str, str]]: (语言, 代码) 元组，如果没有代码块则返回 None
    """
    if not message or "content" not in message:
        return None
    
    code_blocks = parse_code(message["content"])
    return code_blocks[0] if code_blocks else None

def is_executable_language(language: str) -> bool:
    """
    判断语言是否可执行
    
    Args:
        language: 语言标识
        
    Returns:
        bool: 是否可执行
    """
    # 当前支持的可执行语言
    executable_languages = {"python", "r", "javascript", "bash", "sql"}
    return language.lower() in executable_languages