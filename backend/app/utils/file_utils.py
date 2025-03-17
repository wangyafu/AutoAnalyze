"""
文件操作工具模块

提供文件类型判断、文件大小格式化等功能
"""
import os
import mimetypes
from pathlib import Path
from typing import Optional, Union, Dict, List

# 初始化 mimetypes
mimetypes.init()

# 文本文件的 MIME 类型前缀
TEXT_MIME_PREFIXES = [
    "text/",
    "application/json",
    "application/xml",
    "application/javascript",
    "application/x-javascript",
    "application/typescript",
]

# 文件类型分类
FILE_TYPE_CATEGORIES = {
    "code": [
        ".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp", ".h", ".hpp",
        ".cs", ".php", ".rb", ".go", ".rs", ".swift", ".kt", ".scala", ".sh", ".bat",
        ".ps1", ".r", ".sql", ".tsx", ".jsx"
    ],
    "data": [
        ".csv", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".conf", ".cfg",
        ".xls", ".xlsx", ".db", ".sqlite", ".sqlite3", ".parquet", ".feather", ".arrow",
        ".hdf5", ".h5", ".dat"
    ],
    "document": [
        ".txt", ".md", ".markdown", ".rst", ".tex", ".pdf", ".doc", ".docx", ".rtf",
        ".odt", ".ppt", ".pptx", ".odp"
    ],
    "image": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".ico"
    ],
    "audio": [
        ".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"
    ],
    "video": [
        ".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"
    ],
    "archive": [
        ".zip", ".rar", ".tar", ".gz", ".7z", ".bz2", ".xz"
    ]
}

# 二进制文件扩展名
BINARY_EXTENSIONS = [
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".mp3", ".wav", ".mp4", 
    ".avi", ".mov", ".zip", ".rar", ".tar.gz", ".exe", ".dll", ".so",
    ".pyc", ".pyd", ".obj", ".bin", ".dat", ".iso", ".img"
]

def get_file_type(path: Union[str, Path]) -> str:
    """
    获取文件类型
    
    Args:
        path: 文件路径
        
    Returns:
        str: 文件类型分类 ("code", "data", "document", "image", "audio", "video", "archive", "other")
    """
    if isinstance(path, str):
        path = Path(path)
    
    extension = path.suffix.lower()
    
    # 根据扩展名判断文件类型
    for category, extensions in FILE_TYPE_CATEGORIES.items():
        if extension in extensions:
            return category
    
    # 如果扩展名无法判断，尝试使用 mimetypes 模块
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type:
        if mime_type.startswith("text/"):
            return "document"
        elif mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("audio/"):
            return "audio"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("application/"):
            if any(keyword in mime_type for keyword in ["zip", "compressed", "archive", "tar"]):
                return "archive"
            elif any(keyword in mime_type for keyword in ["json", "xml"]):
                return "data"
            elif any(keyword in mime_type for keyword in ["javascript", "typescript"]):
                return "code"
    
    return "other"

def is_text_file(path: Union[str, Path]) -> bool:
    """
    判断是否为文本文件
    
    Args:
        path: 文件路径
        
    Returns:
        bool: 是否为文本文件
    """
    if isinstance(path, str):
        path = Path(path)
    
    # 检查文件是否存在
    if not path.exists() or not path.is_file():
        return False
    
    # 根据扩展名快速判断
    extension = path.suffix.lower()
    if extension in BINARY_EXTENSIONS:
        return False
    
    # 使用 mimetypes 判断 MIME 类型
    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type:
        for prefix in TEXT_MIME_PREFIXES:
            if mime_type.startswith(prefix):
                return True
    
    # 如果 mimetypes 无法判断，尝试读取文件前几个字节
    try:
        with open(path, 'rb') as f:
            content = f.read(1024)
            # 检查是否包含空字节，文本文件通常不包含
            return b'\x00' not in content
    except Exception:
        pass
    
    return False

def format_file_size(size: int) -> str:
    """
    格式化文件大小
    
    Args:
        size: 文件大小（字节）
        
    Returns:
        str: 格式化后的文件大小
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}" if unit != 'B' else f"{size} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"

def get_file_extension(path: Union[str, Path]) -> str:
    """
    获取文件扩展名
    
    Args:
        path: 文件路径
        
    Returns:
        str: 文件扩展名（不包含点）
    """
    if isinstance(path, str):
        path = Path(path)
    
    return path.suffix.lstrip('.')

def get_safe_filename(filename: str) -> str:
    """
    获取安全的文件名（移除不安全字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 安全的文件名
    """
    # 移除不安全字符
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename

def list_directory(path: Union[str, Path], include_hidden: bool = False) -> List[Dict]:
    """
    列出目录内容
    
    Args:
        path: 目录路径
        include_hidden: 是否包含隐藏文件
        
    Returns:
        List[Dict]: 目录内容列表，每个元素包含 name, type, size, modified 等信息
    """
    if isinstance(path, str):
        path = Path(path)
    
    if not path.exists() or not path.is_dir():
        return []
    
    result = []
    for item in path.iterdir():
        # 跳过隐藏文件
        if not include_hidden and item.name.startswith('.'):
            continue
        
        try:
            stats = item.stat()
            file_info = {
                "name": item.name,
                "path": str(item.relative_to(path.parent)),
                "type": "directory" if item.is_dir() else get_file_type(item),
                "size": format_file_size(stats.st_size) if not item.is_dir() else None,
                "modified": stats.st_mtime,
                "is_dir": item.is_dir()
            }
            result.append(file_info)
        except Exception:
            # 忽略无法访问的文件
            continue
    
    # 先显示目录，再显示文件，按名称排序
    return sorted(result, key=lambda x: (not x["is_dir"], x["name"].lower()))