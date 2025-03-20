import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { OutputItem, ImageItem, ExecutionStatus } from '../types'

export const useCodeExecutionStore = defineStore('codeExecution', () => {
  // 存储所有代码执行的状态
  const executionStatus = ref<{[key: string]: ExecutionStatus}>({})
  
  // 初始化执行状态
  function initExecution(executionId: string) {
    executionStatus.value[executionId] = {
      status: 'running',
      output: [],
      images: []
    }
  }
  
  // 更新执行状态
  function updateExecutionStatus(executionId: string, status: 'running' | 'completed' | 'error') {
    if (executionStatus.value[executionId]) {
      executionStatus.value[executionId].status = status
    }
  }
  
  // 添加输出
  function addOutput(executionId: string, output: OutputItem) {
    if (executionStatus.value[executionId]) {
      executionStatus.value[executionId].output.push(output)
      
      // 如果是图片类型，也添加到图片列表
      if (output.type === 'image') {
        const imageData: ImageItem = {
          type: 'image',
          format: 'png', // 默认格式
          data: output.content
        }
        executionStatus.value[executionId].images.push(imageData)
      }
    }
  }
  
  // 添加图片
  function addImage(executionId: string, imageData: ImageItem) {
    if (executionStatus.value[executionId]) {
      executionStatus.value[executionId].images.push(imageData)
    }
  }
  
  // 设置错误信息
  function setError(executionId: string, error: string) {
    if (executionStatus.value[executionId]) {
      executionStatus.value[executionId].error = error
      executionStatus.value[executionId].status = 'error'
    }
  }
  
  // 取消执行
  function cancelExecution(executionId: string) {
    // 这里只更新状态，实际的取消操作需要通过websocket发送到后端
    if (executionStatus.value[executionId]) {
      executionStatus.value[executionId].status = 'error'
      executionStatus.value[executionId].error = '执行已取消'
    }
  }
  
  return {
    executionStatus,
    initExecution,
    updateExecutionStatus,
    addOutput,
    addImage,
    setError,
    cancelExecution
  }
})