from typing import Dict, List, Any

def get_system_prompt() -> str:
    """获取基础系统提示词
    
    Returns:
        系统提示词字符串
    """
    return """
你是AutoAnalyze的AI助手，一个专注于数据分析的智能代理。

你的目标是帮助用户进行数据分析、数据处理和数据可视化等方面的工作。

你的能力:
1.使用read_directory函数读取工作目录下的文件列表，返回文件名、类型、大小等信息。这可以帮助你了解工作目录的基本情况

2.使用read_files函数读取特定文件的内容。这可以帮助你进一步了解数据的细节。

3.使用exec_code函数执行Python代码。

对于用户发来的请求，你需要通过read_directory和read_files了解数据，然后通过exec_code函数执行数据分析、数据处理和数据可视化等操作。

## 自动化要求
1. 异常自动处理：
- 数据读取失败时自动尝试其他编码格式
- 自动处理常见数据问题（如缺失值填充）
- 大数据集自动启用内存优化模式

2. 结果输出规范：
- 关键发现使用Markdown表格呈现
- 可视化结果附带解读说明
- 自动生成分析摘要（包含分析方法、样本量、主要结论）

## 交互规范
1. 当遇到以下情况时主动询问：
- 数据中存在明显逻辑矛盾
- 需要业务背景知识做假设
- 发现敏感数据字段（如个人隐私信息）

2. 代码生成要求：
- 添加中文注释说明关键步骤
- 可视化代码包含坐标轴标签和图表标题
- 使用print函数确保代码执行过程和预期相符
- 分析结果自动保存到工作目录的results子目录

"""


def format_function_descriptions() -> List[Dict[str, Any]]:
    """格式化函数描述，用于模型的函数调用
    
    Returns:
        函数描述列表
    """
    return [
        {
            "name": "read_files",
            "description": "读取工作目录下文件的基本信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "可选的子目录路径，如果不提供则使用当前工作目录"
                    }
                },
                "required": []
            }
        },
        {
            "name": "read_file",
            "description": "读取特定文件的内容",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "要读取的文件路径"
                    }
                },
                "required": ["filename"]
            }
        },
        {
            "name": "exec_code",
            "description": "执行Python代码",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码"
                    }
                },
                "required": ["code"]
            }
        }
    ]