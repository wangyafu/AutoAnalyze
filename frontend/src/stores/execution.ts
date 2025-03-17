// 执行状态管理
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Execution, ExecutionOutput } from '../types/execution';
import { executeCode, cancelExecution, subscribeExecution } from '../api/execution';

export const useExecutionStore = defineStore('execution', () => {
  // 状态
  const executions = ref<Execution[]>([]);
  const currentExecution = ref<Execution | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // 计算属性
  const isExecuting = computed(() => {
    return currentExecution.value?.status === 'pending' || currentExecution.value?.status === 'running';
  });
  
  // 执行代码
  async function executeCodeAction(conversationId: string, code: string, codeBlockId?: string) {
    loading.value = true;
    error.value = null;
    
    try {
      // 创建执行记录
      const response = await executeCode(conversationId, code);
      const executionId = response.execution_id;
      
      // 创建执行对象
      const execution: Execution = {
        id: executionId,
        conversation_id: conversationId,
        code,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        outputs: []
      };
      
      // 添加到执行列表
      executions.value.unshift(execution);
      currentExecution.value = execution;
      
      // 订阅执行结果
      subscribeToExecution(executionId);
      
      return executionId;
    } catch (err) {
      console.error('执行代码失败:', err);
      error.value = '执行代码失败';
      return null;
    } finally {
      loading.value = false;
    }
  }
  
  // 取消执行
  async function cancelExecutionAction() {
    if (!currentExecution.value) return;
    
    try {
      await cancelExecution(currentExecution.value.id);
      updateExecutionStatus(currentExecution.value.id, 'cancelled');
    } catch (err) {
      console.error('取消执行失败:', err);
      error.value = '取消执行失败';
    }
  }
  
  // 订阅执行结果
  function subscribeToExecution(executionId: string) {
    // 订阅执行状态更新
    subscribeExecution(executionId, (data) => {
      if (data.status) {
        // 状态更新
        updateExecutionStatus(executionId, data.status);
      } else if (data.output_type) {
        // 输出更新
        const output: ExecutionOutput = {
          id: `output-${Date.now()}`,
          execution_id: executionId,
          type: data.output_type,
          content: data.content,
          timestamp: data.timestamp
        };
        
        addExecutionOutput(executionId, output);
      }
    });
  }
  
  // 更新执行状态
  function updateExecutionStatus(id: string, status: string) {
    const execution = executions.value.find(exec => exec.id === id);
    
    if (execution) {
      execution.status = status as any;
      execution.updated_at = new Date().toISOString();
      
      if (status === 'completed' || status === 'error' || status === 'cancelled') {
        if (currentExecution.value?.id === id) {
          currentExecution.value = null;
        }
      }
    }
  }
  
  // 添加执行输出
  function addExecutionOutput(id: string, output: ExecutionOutput) {
    const execution = executions.value.find(exec => exec.id === id);
    
    if (execution) {
      execution.outputs.push(output);
    }
  }
  
  return {
    // 状态
    executions,
    currentExecution,
    loading,
    error,
    
    // 计算属性
    isExecuting,
    
    // 方法
    executeCode: executeCodeAction,
    cancelExecution: cancelExecutionAction
  };
});