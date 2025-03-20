import asyncio
import uuid
import sys
import traceback
from typing import Dict, Any, Optional, Callable, List
import time
import os
from queue import Empty  # 添加导入
from jupyter_client.asynchronous import AsyncKernelClient
from jupyter_client import AsyncKernelManager
from app.utils.logger import get_logger

logger = get_logger(__name__)

class JupyterExecutionEngine:
    """基于Jupyter内核的代码执行引擎，负责安全地执行用户代码"""

    def __init__(self):
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.output_callbacks: Dict[str, Callable] = {}
        self.environments: Dict[str, Dict[str, Any]] = {}  # 会话环境存储
        # 修改为单个全局内核
        self.kernel_manager: Optional[AsyncKernelManager] = None
        self.kernel_client: Optional[AsyncKernelClient] = None
        self.execution_tasks: Dict[str, asyncio.Task] = {}  # 存储执行任务
        self.setup_code="""
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置默认字体为 SimHei（黑体）
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题"""   

    async def create_kernel(self, conversation_id: str) -> None:
        """创建全局Jupyter内核"""
        # 如果内核已存在，直接返回
        if self.kernel_manager is not None:
            return

        try:
            km = AsyncKernelManager(kernel_name='python3')
            await km.start_kernel()
            client = km.client()
            client.start_channels()

            # 新增：验证内核准备就绪
            await client.wait_for_ready(timeout=10)

#             setup_code = """
# import matplotlib.pyplot as plt
# plt.switch_backend('agg')  # 非交互式模式下使用agg后端
# """
  
            client.execute(self.setup_code)#避免出现字体错误

            # 保存全局内核引用
            self.kernel_manager = km
            self.kernel_client = client

        except Exception as e:
            logger.error(f"创建内核失败: {str(e)}")
            # 尝试使用默认内核
            try:
                km = AsyncKernelManager()
                await km.start_kernel()
                client = km.client()
                client.start_channels()

                client.execute(self.setup_code)

                # 保存全局内核引用
                self.kernel_manager = km
                self.kernel_client = client

            except Exception as e:
                logger.error(f"使用默认内核也失败: {str(e)}")
                raise e

    async def execute_code(self, code: str, execution_id: str, conversation_id: str, workspace: Optional[str] = None) -> str:
        """执行代码并返回执行ID

        Args:
            code: 要执行的代码
            execution_id: 执行ID，如果为None则自动生成
            conversation_id: 关联的对话ID
            workspace: 工作目录

        Returns:
            execution_id: 执行ID
        """
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # 确保会话有对应的内核
        await self.create_kernel(conversation_id)

        # 创建执行记录
        self.executions[execution_id] = {
            "status": "pending",
            "code": code,
            "conversation_id": conversation_id,
            "start_time": None,
            "end_time": None,
            "output": [],
            "error": None,
            "images": [],  # 存储生成的图片
            "execution_count": None,  # 记录执行计数
            "is_executing": False  # 标记是否正在执行
        }

        # 创建异步执行任务并存储
        task = asyncio.create_task(self._execute_code_async(code, execution_id, workspace, conversation_id))
        self.execution_tasks[execution_id] = task
        
        return execution_id

    async def _execute_code_async(self, code: str, execution_id: str, workspace: Optional[str], conversation_id: str):
        """异步执行代码"""
        original_cwd = os.getcwd()
        msg_id = None  # 用于跟踪当前执行的消息ID

        try:
            kernel = self.kernel_manager
            client = self.kernel_client
            setup_code = ""

            # 更新状态为运行中
            self.executions[execution_id]["status"] = "running"

            # 切换工作目录
            if workspace:
                os.chdir(workspace)
                # 设置内核的工作目录
                setup_code += f"\nimport os\nos.chdir('{workspace.replace('\\', '/')}')\n"
                logger.info(f"设置工作目录: {setup_code}")

            # 发送代码到内核执行
            self.executions[execution_id]["is_executing"] = True
            msg_id = client.execute(setup_code + code)
            logger.info(f"代码执行msg_id={msg_id}")

            # 处理执行结果
            execution_started = False

            while True:
                try:
                    msg = await client.get_iopub_msg(timeout=1.0)
        
                    # 关键修复：验证消息属于当前执行
                    parent_header = msg.get('parent_header', {})
                    current_msg_id = parent_header.get('msg_id')
                    if current_msg_id != msg_id:
                        logger.debug("跳过非当前执行的消息")
                        continue

                    logger.debug(f"接收到消息: {msg['header']['msg_type']}")
                    msg_type = msg['header']['msg_type']
                    content = msg['content']

                    if msg_type == 'execute_input':
                        execution_started = True
                        self.executions[execution_id]["start_time"] = time.time()
                        self.executions[execution_id]["execution_count"] = content.get('execution_count')

                    elif msg_type == 'stream':
                        # 处理标准输出/错误
                        stream_name = content['name']  # stdout或stderr
                        text = content['text']
                        await self._add_output(execution_id, text, stream_name)

                    elif msg_type == 'display_data' or msg_type == 'execute_result':
                        # 处理富文本输出（包括图片）
                        data = content['data']
                        if 'image/png' in data:
                            # 保存图片数据
                            self.executions[execution_id]['images'].append({
                                'data': data['image/png'],
                                'format': 'png'
                            })
                        elif 'text/plain' in data:
                            await self._add_output(execution_id, data['text/plain'], 'output')

                    elif msg_type == 'error':
                        # 处理错误信息
                        error_msg = '\n'.join(content['traceback'])
                        await self._add_output(execution_id, error_msg, 'error')
                        self.executions[execution_id]['status'] = 'error'
                        self.executions[execution_id]['error'] = error_msg
                        self.executions[execution_id]['is_executing'] = False

                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        # 只有在执行已经开始后，idle状态才表示执行完成
                        if execution_started:
                            if self.executions[execution_id]['status'] != 'error':
                                self.executions[execution_id]['status'] = 'completed'
                            self.executions[execution_id]['is_executing'] = False
                            logger.info(f"代码执行完成: {execution_id}")
                            break

                except Empty:
                    # 处理队列空的情况
                    if execution_started and not self.executions[execution_id]['is_executing']:
                        logger.info(f"执行已完成，退出监听循环: {execution_id}")
                        break
                    logger.debug("IOPub通道无新消息，继续等待...")
                    continue
                except asyncio.TimeoutError:
                    # 超时处理
                    if execution_started and not self.executions[execution_id]['is_executing']:
                        logger.info(f"执行可能已完成，退出循环")
                        break
                    continue
                except Exception as e:
                    logger.error(f"处理消息出错: {str(e)}")
                    self.executions[execution_id]['status'] = 'error'
                    self.executions[execution_id]['error'] = str(e)
                    break

            self.executions[execution_id]['end_time'] = time.time()

        except Exception as e:
            logger.error(f"执行异常: {str(e)}")
            self.executions[execution_id]['status'] = 'error'
            self.executions[execution_id]['error'] = f"执行异常: {str(e)}"
            self.executions[execution_id]['end_time'] = time.time()
            self.executions[execution_id]['is_executing'] = False
            raise e

        finally:
            if workspace:
                os.chdir(original_cwd)

    async def _add_output(self, execution_id: str, output: str, output_type: str = 'stdout'):
        """添加执行输出"""
        if execution_id in self.executions:
            output_item = {
                'type': output_type,
                'content': output,
                'timestamp': time.time()
            }
            self.executions[execution_id]['output'].append(output_item)

            # 调用回调函数（如果有）
            if execution_id in self.output_callbacks:
                await self.output_callbacks[execution_id](output_item)

    async def cancel_execution(self, execution_id: str) -> bool:
        """取消代码执行

        Args:
            execution_id: 执行ID

        Returns:
            bool: 是否成功取消
        """
        if execution_id not in self.executions:
            return False

        execution = self.executions[execution_id]
        if execution['status'] not in ['running', 'pending']:
            return False

        # 中断内核执行
        conversation_id = execution['conversation_id']
        if self.kernel_client:
            await self.kernel_client.interrupt_kernel()

        # 取消执行任务
        if execution_id in self.execution_tasks:
            task = self.execution_tasks[execution_id]
            if not task.done():
                task.cancel()

        # 更新状态为取消
        execution['status'] = 'cancelled'
        execution['end_time'] = time.time()
        execution['is_executing'] = False

        # 添加取消消息到输出
        await self._add_output(execution_id, '执行已取消', 'system')

        return True

    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """获取执行状态

        Args:
            execution_id: 执行ID

        Returns:
            Dict: 执行状态信息，如果不存在则返回None
        """
        if execution_id not in self.executions:
            return None

        execution = self.executions[execution_id]

        # 创建状态副本，不包含不需要的字段
        status = execution.copy()
        if 'is_executing' in status:
            del status['is_executing']

        return status

    def register_output_callback(self, execution_id: str, callback: Callable):
        """注册输出回调函数

        Args:
            execution_id: 执行ID
            callback: 回调函数，接收输出项作为参数
        """
        self.output_callbacks[execution_id] = callback

    def unregister_output_callback(self, execution_id: str):
        """注销输出回调函数

        Args:
            execution_id: 执行ID
        """
        if execution_id in self.output_callbacks:
            del self.output_callbacks[execution_id]

    async def cleanup(self):
        """清理所有内核资源"""
        # 等待所有执行任务完成或取消
        if self.execution_tasks:
            logger.info(f"等待 {len(self.execution_tasks)} 个执行任务完成...")
            pending_tasks = [task for task in self.execution_tasks.values() if not task.done()]
            
            if pending_tasks:
                # 等待所有任务完成，或设置超时
                try:
                    await asyncio.wait(pending_tasks, timeout=5.0)
                except asyncio.TimeoutError:
                    # 超时后取消剩余任务
                    for task in pending_tasks:
                        if not task.done():
                            task.cancel()
                    
                    # 等待取消操作完成
                    if pending_tasks:
                        await asyncio.wait(pending_tasks, timeout=2.0)
            
            logger.info("所有执行任务已处理完毕")
        
        # 关闭内核资源
        if self.kernel_client:
            self.kernel_client.shutdown()
        if self.kernel_manager:
            await self.kernel_manager.shutdown_kernel(now=True)
        self.kernel_client = None
        self.kernel_manager = None

# 创建全局执行引擎实例
jupyter_execution_engine = JupyterExecutionEngine()

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async def main():
        await jupyter_execution_engine.create_kernel("test")
        await jupyter_execution_engine.execute_code("print('hello')", "a", "b", "D:/")
        await jupyter_execution_engine.cleanup()

    # 使用 asyncio.run 运行主函数
    asyncio.run(main())