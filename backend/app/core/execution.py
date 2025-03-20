import asyncio
import uuid
import sys
import traceback
from typing import Dict, Any, Optional, Callable
import threading
import time
import os
from app.utils.logger import get_logger
from jupyter_client import KernelManager
from queue import Empty

logger = get_logger(__name__)

class ExecutionEngine:
    """代码执行引擎，负责安全地执行用户代码"""
    
    def __init__(self):
        self.executions: Dict[str, Dict[str, Any]] = {}
        self.output_callbacks: Dict[str, Callable] = {}
        self.environments: Dict[str, Dict[str, Any]] = {}  # 会话环境存储
        self.kernels: Dict[str, Any] = {}  # 存储每个会话的内核
        self.lock = threading.Lock()  # 线程锁
        
    def _create_kernel(self, conversation_id: str) -> None:
        """为会话创建新的Jupyter内核"""
        if conversation_id not in self.kernels:
            km = KernelManager()
            km.start_kernel()
            client = km.client()
            client.start_channels()
            
            self.kernels[conversation_id] = {
                'manager': km,
                'client': client
            }

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
        with self.lock:
            self._create_kernel(conversation_id)
            
        # 创建执行记录
        self.executions[execution_id] = {
            "status": "running",
            "code": code,
            "conversation_id": conversation_id,
            "start_time": time.time(),
            "end_time": None,
            "output": [],
            "error": None,
            "thread": None,
            "images": []  # 存储生成的图片
        }
        
        # 在新线程中执行代码
        thread = threading.Thread(
            target=self._execute_code_thread,
            args=(code, execution_id, workspace, conversation_id)
        )
        thread.daemon = True
        thread.start()
        
        self.executions[execution_id]["thread"] = thread
        
        return execution_id
    
    def _execute_code_thread(self, code: str, execution_id: str, workspace: Optional[str], conversation_id: str):
        """在独立线程中执行代码"""
        kernel = self.kernels[conversation_id]
        client = kernel['client']
        
        try:
            # 切换工作目录
            original_cwd = os.getcwd()
            if workspace:
                os.chdir(workspace)
                # 设置内核的工作目录
                setup_code = f"import os; os.chdir('{workspace.replace('\\', '/')}')"
                client.execute(setup_code, silent=True)
            
            # 发送代码到内核执行
            msg_id = client.execute(code)
            
            # 处理执行结果
            while True:
                try:
                    msg = client.get_iopub_msg(timeout=1)
                    msg_type = msg['header']['msg_type']
                    content = msg['content']
                    
                    if msg_type == 'stream':
                        # 处理标准输出/错误
                        stream_name = content['name']  # stdout或stderr
                        text = content['text']
                        self._add_output(execution_id, text, stream_name)
                        
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
                            self._add_output(execution_id, data['text/plain'], 'output')
                            
                    elif msg_type == 'error':
                        # 处理错误信息
                        error_msg = '\n'.join(content['traceback'])
                        self._add_output(execution_id, error_msg, 'error')
                        self.executions[execution_id]['status'] = 'error'
                        self.executions[execution_id]['error'] = error_msg
                        break
                        
                    elif msg_type == 'status' and content['execution_state'] == 'idle':
                        # 执行完成
                        if self.executions[execution_id]['status'] != 'error':
                            self.executions[execution_id]['status'] = 'completed'
                        break
                        
                except Empty:
                    continue
                except Exception as e:
                    logger.error(f"处理执行结果时出错: {str(e)}")
                    self.executions[execution_id]['status'] = 'error'
                    self.executions[execution_id]['error'] = str(e)
                    break
            
            self.executions[execution_id]['end_time'] = time.time()
            
        except Exception as e:
            logger.error(f"执行线程异常: {str(e)}")
            self.executions[execution_id]['status'] = 'error'
            self.executions[execution_id]['error'] = f"执行线程异常: {str(e)}"
            self.executions[execution_id]['end_time'] = time.time()
            
        finally:
            if workspace:
                os.chdir(original_cwd)
    
    def _handle_print(self, execution_id: str, *args, **kwargs):
        """处理代码中的print函数调用"""
        # 获取分隔符和结束符
        sep = kwargs.get("sep", " ")
        end = kwargs.get("end", "\n")
        
        # 将参数转换为字符串并连接
        output = sep.join(str(arg) for arg in args) + end
        
        # 添加到输出
        self._add_output(execution_id, output, "stdout")
    
    def _add_output(self, execution_id: str, output: str, output_type: str = "stdout"):
        """添加执行输出"""
        if execution_id in self.executions:
            output_item = {
                "type": output_type,
                "content": output,
                "timestamp": time.time()
            }
            self.executions[execution_id]["output"].append(output_item)
            
            # 调用回调函数（如果有）
            if execution_id in self.output_callbacks:
                self.output_callbacks[execution_id](output_item)
    
    def cancel_execution(self, execution_id: str) -> bool:
        """取消代码执行
        
        Args:
            execution_id: 执行ID
            
        Returns:
            bool: 是否成功取消
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        if execution["status"] not in ["running", "pending"]:
            return False
        
        # 更新状态为取消
        execution["status"] = "cancelled"
        execution["end_time"] = time.time()
        
        # 添加取消消息到输出
        self._add_output(execution_id, "执行已取消", "system")
        
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
        
        # 创建状态副本，不包含线程对象
        status = execution.copy()
        if "thread" in status:
            del status["thread"]
        
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

# 创建全局执行引擎实例
execution_engine = ExecutionEngine()

if __name__ == "__main__":
    # 测试基本执行功能
    test_code = "print('Hello World')"
    execution_id = execution_engine.execute_code(
        code=test_code,
        execution_id="test_1",
        conversation_id="convo_1"
    )
    
    # 等待执行完成
    time.sleep(0.5)
    status = execution_engine.get_execution_status(execution_id)
    print("\n测试用例1 - 基本执行:")
    print(f"状态: {status['status']}")
    print(f"输出: {[o['content'] for o in status['output']]}")

    # 测试变量持久化（会话环境）
    execution_id2 = execution_engine.execute_code(
        code="x = 42\nprint(x)",
        execution_id="test_2",
        conversation_id="convo_1"  # 使用相同会话ID
    )
    time.sleep(0.5)
    
    execution_id3 = execution_engine.execute_code(
        code="print(x*2)",
        execution_id="test_3",
        conversation_id="convo_1"  # 继续使用相同会话ID
    )
    time.sleep(0.5)
    
    print("\n测试用例2 - 变量持久化:")
    print("第二次执行输出:", [o['content'] for o in execution_engine.get_execution_status(execution_id2)['output']])
    print("第三次执行输出:", [o['content'] for o in execution_engine.get_execution_status(execution_id3)['output']])

    # 测试错误处理
    error_code = "print(1/0)"
    execution_engine.execute_code(
        code=error_code,
        execution_id="test_error",
        conversation_id="convo_2"
    )
    time.sleep(0.5)
    print("\n测试用例3 - 错误处理:")
    print(execution_engine.get_execution_status("test_error")['error'])

    # 测试取消功能
    long_running_code = "import time\nfor i in range(10):\n    time.sleep(0.2)"
    execution_engine.execute_code(
        code=long_running_code,
        execution_id="test_cancel",
        conversation_id="convo_3"
    )
    time.sleep(0.3)  # 等待执行开始
    execution_engine.cancel_execution("test_cancel")
    time.sleep(0.5)
    print("\n测试用例4 - 取消执行:")
    print(execution_engine.get_execution_status("test_cancel")['status'])
    print("输出:", [o['content'] for o in execution_engine.get_execution_status("test_cancel")['output']])