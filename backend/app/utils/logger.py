import logging
import os
from pathlib import Path
from typing import Optional, Union, List

# 日志级别映射
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL
}

def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[str] = "app.log",#app.log
    log_format: Optional[str] = None,
    log_dir: Optional[Union[str, Path]] = None
) -> None:
    """设置日志配置
    
    Args:
        level: 日志级别，可以是整数或字符串("debug", "info", "warning", "error", "critical")
        log_file: 日志文件名，如果为None则不记录到文件
        log_format: 日志格式，如果为None则使用默认格式
        log_dir: 日志目录，如果为None则使用当前目录
    """
    # 处理日志级别
    if isinstance(level, str):
        level = LOG_LEVELS.get(level.lower(), logging.INFO)
    
    # 设置日志格式
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 准备处理器列表
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        # 如果指定了日志目录，确保目录存在
        if log_dir:
            if isinstance(log_dir, str):
                log_dir = Path(log_dir)
            log_dir.mkdir(exist_ok=True)
            log_path = log_dir / log_file
        else:
            log_path = log_file
        
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    
    # 配置日志
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=handlers
    )

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """获取日志器
    
    Args:
        name: 日志器名称，如果为None则返回根日志器
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)

def get_module_logger() -> logging.Logger:
    """获取当前模块的日志器
    
    自动使用调用者的模块名作为日志器名称
    
    Returns:
        logging.Logger: 日志器实例
    """
    import inspect
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    return get_logger(module.__name__ if module else None)