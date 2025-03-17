// 代码执行管理
import { ref, computed } from 'vue';
import { useExecutionStore } from '../stores/execution';
import type { ExecutionOutput } from '../types/execution'; // 导入输出类型

export function useCodeExecution() {
  const executionStore = useExecutionStore();
  const output = ref<ExecutionOutput[]>([]); // 明确指定类型为ExecutionOutput数组
  
  // 是否正在执行
  const isExecuting = computed(() => executionStore.isExecuting);
  
  // 执行代码
  const executeCode = async (conversationId: string, code: string, codeBlockId?: string) => {
    // 清空输出
    output.value = [];
    
    // 调用store执行代码
    const executionId = await executionStore.executeCode(conversationId, code, codeBlockId);
    
    if (executionId) {
      // 监听执行输出
      const execution = executionStore.executions.find(exec => exec.id === executionId);
      if (execution) {
        // 将输出添加到本地输出列表
        output.value = execution.outputs;
      }
    }
    
    return executionId;
  };
  
  // 取消执行
  const cancelExecution = async () => {
    await executionStore.cancelExecution();
  };
  
  return {
    isExecuting,
    output,
    executeCode,
    cancelExecution
  };
}