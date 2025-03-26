import os
import base64
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, Union
from openai import AsyncOpenAI
from app.config import get_settings

async def encode_image_to_base64(image_path: str) -> str:
    """
    将图片编码为base64格式
    
    Args:
        image_path: 图片文件路径
        
    Returns:
        str: base64编码的图片URL
    
    Raises:
        FileNotFoundError: 图片文件不存在时抛出
        Exception: 读取或编码过程中出错时抛出
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")
    
    try:
        # 获取文件扩展名
        file_ext = os.path.splitext(image_path)[1].lstrip('.')
        if not file_ext:
            file_ext = "png"  # 默认扩展名
        
        # 读取图片并编码 - 使用异步文件IO
        image_data = await asyncio.to_thread(lambda: open(image_path, "rb").read())
        
        # 生成base64编码的图片URL
        image_url = f"data:image/{file_ext};base64,{base64.b64encode(image_data).decode('utf-8')}"
        return image_url
    
    except Exception as e:
        raise Exception(f"图片编码失败: {str(e)}")

async def analyze_image(image_data: Union[str, bytes], image_format: str = "png", prompt: str = "为了进行数据分析任务我制作一张图片。请描述图片的内容。只要包含图片中关于数据的内容，不要有进一步的推断。", is_base64: bool = True) -> str:
    """
    使用视觉模型分析图片内容
    
    Args:
        image_data: 图片数据，可以是文件路径(str)或base64编码的数据(str)或原始字节数据(bytes)
        image_format: 图片格式，如png、jpg等，当提供base64或字节数据时使用
        prompt: 给模型的提示文本
        is_base64: 是否已经是base64编码，True表示image_data已经是base64编码
        
    Returns:
        str: 模型返回的分析结果
        
    Raises:
        Exception: 处理过程中出错时抛出
    """
    try:
        # 获取配置
        settings = get_settings()
        vision_config = settings.vision_model
        
        # 检查视觉模型配置是否完整
        if not vision_config.api_key or not vision_config.endpoint or not vision_config.model:
            return "视觉模型未配置，无法分析图片。请在设置中配置视觉模型后重试。"
        
        # 处理图片数据
        if isinstance(image_data, str) and not is_base64:
            # 如果是文件路径，则编码图片
            image_url = await encode_image_to_base64(image_data)
        elif isinstance(image_data, str) and is_base64:
            # 如果已经是base64编码，则直接构建URL
            image_url = f"data:image/{image_format};base64,{image_data}"
        elif isinstance(image_data, bytes):
            # 如果是字节数据，则进行base64编码
            image_url = f"data:image/{image_format};base64,{base64.b64encode(image_data).decode('utf-8')}"
        else:
            raise ValueError("不支持的图片数据类型")
        
        try:
            # 创建异步客户端
            client = AsyncOpenAI(
                api_key=vision_config.api_key,
                base_url=vision_config.endpoint
            )
            
            # 发送异步请求
            completion = await client.chat.completions.create(
                model=vision_config.model,
                messages=[
                    {"role": "system", "content": "你是一个图像分析助手。"},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    },
                ],
            )
            
            return completion.choices[0].message.content
            
        except Exception as e:
            return f"视觉模型调用失败: {str(e)}。请检查视觉模型配置是否正确。"
    
    except Exception as e:
        raise Exception(f"图片分析失败: {str(e)}")

if __name__ == "__main__":
    # 测试异步代码
    async def main():
        try:
            test_image_path = r"D:\deep\examples\exam\数学成绩分布.png"  # 替换为实际测试图片路径
            result = await analyze_image(test_image_path, is_base64=False)
            print(result)
        except Exception as e:
            print(f"错误: {str(e)}")
    
    # 运行异步主函数
    asyncio.run(main())