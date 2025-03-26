from typing import Dict, List, Optional, Any, Union
from app.core.jupyter_execution import jupyter_execution_engine as execution_engine
import uuid
from app.websocket.manager import manager
import asyncio

from app.core.filesystem import FileSystemManager
from app.core.image_utils import analyze_image
import logging
import sys
import io
import time
import traceback
import re
import base64
logger = logging.getLogger(__name__)
# 获取文件系统管理器实例
fs_manager = FileSystemManager()

async def exec_code(code: str, conversation_id: str) -> Dict[str, Any]:
    try:
        if not fs_manager.workspace:
            return {"status": "error", "message": "工作目录未设置"}

        execution_id = str(uuid.uuid4())

        # 创建异步回调函数
        async def async_output_callback(output_item):
            await manager.broadcast_message({
                "type": "code_execution_output",
                "data": {
                    "execution_id": execution_id,
                    "conversation_id": conversation_id,
                    "output": output_item,
                    "timestamp": time.time()
                }
            })


        # 在注册回调前添加日志
        logger.info(f"注册执行回调: {execution_id}")
        execution_engine.register_output_callback(execution_id, async_output_callback)

        # 发送执行开始消息
        await manager.broadcast_message({
            "type": "code_execution_start",
            "data": {
                "execution_id": execution_id,
                "conversation_id": conversation_id,
                "code": code,
                "timestamp": time.time()
            }
        })

        # 直接使用异步方法执行代码，不再使用to_thread
        await execution_engine.execute_code(
            code=code,
            execution_id=execution_id,
            conversation_id=conversation_id,
            workspace=fs_manager.workspace
        )

        # 等待执行完成 - 使用改进的判断逻辑
        while True:
            status = execution_engine.get_execution_status(execution_id)
            if status["start_time"] and(status["status"] not in ["running", "pending"]):
                break
            # 如果有execution_count但状态仍为running，说明已经开始执行
            # 如果is_executing为False，说明执行已完成

            await asyncio.sleep(0.1)

        # 检查是否有图片输出并发送到前端
        image_descriptions = []
        if "images" in status and status["images"]:
            for i, img_data in enumerate(status["images"]):
                # 分析图片内容
                image_description = await analyze_image(
                    image_data=img_data["data"],
                    image_format=img_data["format"],
                    is_base64=True,
                    prompt="这是一个数据可视化图表。请详细描述这个图表展示的内容，包括图表类型、轴标签、数据趋势等关键信息。"
                )
                
                # 保存图片描述
                image_descriptions.append({
                    "index": i,
                    "description": image_description
                })
                
                # 发送图片和描述到前端
                await manager.broadcast_message({
                    "type": "code_execution_image",
                    "data": {
                        "execution_id": execution_id,
                        "conversation_id": conversation_id,
                        "image_data": img_data["data"],
                        "image_format": img_data["format"],
                        "image_index": i,
                        "image_description": image_description,
                        "timestamp": time.time()
                    }
                })

        # 发送执行完成消息
        await manager.broadcast_message({
            "type": "code_execution_end",
            "data": {
                "execution_id": execution_id,
                "conversation_id": conversation_id,
                "status": status["status"],
                "timestamp": time.time()
            }
        })

        # 注销回调函数
        execution_engine.unregister_output_callback(execution_id)

        # 修改输出收集逻辑，改为列表形式
        return {
            "status": "success" if status["status"] == "completed" else "error",
            "output": sorted(
                [
                    {
                        "type": o["type"],
                        "content": o["content"],
                        "timestamp": o["timestamp"]
                    }
                    for o in status["output"]
                ],
                key=lambda x: x["timestamp"]
            ),
            "image_count": len(status.get("images", [])),
            "image_descriptions": image_descriptions
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import asyncio

    # 仅针对Windows系统设置
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def test_exec_code():
        print("\n=== 测试代码执行功能 ===")

        # 设置测试工作目录
        fs_manager.set_workspace("D:\\deep")

        test_cases = [
            {
                "name": "基础打印测试",
                "code": """
print('Hello World!')
print('Testing...')
                """
            },
            {
                "name": "数据处理测试",
                "code": """
import pandas as pd
df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
print(df.describe())
                """
            },
            {
                "name": "图表生成测试",
                "code": """
import matplotlib.pyplot as plt
plt.figure(figsize=(6,4))
plt.plot([1,2,3,4], [1,4,2,3])
plt.title('Test Plot')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.show()
                """
            },
            {
                "name": "错误处理测试",
                "code": """
# 制造一个错误
x = 1/0
                """
            }
        ]

        for test in test_cases:
            print(f"\n--- 测试用例: {test['name']} ---")
            try:
                result = await exec_code(
                    code=test["code"],
                    conversation_id="test-conversation"
                )
                print("执行结果:", result)
                if result["status"] == "error":
                    print("错误信息:", result["message"])
                else:
                    if result.get("stdout"):
                        print("标准输出:", result["stdout"])
                    if result.get("stderr"):
                        print("标准错误:", result["stderr"])
                    if result.get("image_count"):
                        print(f"生成图片数量: {result['image_count']}")
            except Exception as e:
                print(f"测试出错: {str(e)}")


    # 运行测试
    asyncio.run(test_exec_code())
