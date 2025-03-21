<template>
  <div class="mb-4">
    <!-- 用户消息 -->
    <div v-if="message.type === 'user'" class="user-message">
      <div class="flex items-start">
        <div class="user-avatar">
          <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
            <span>U</span>
          </div>
        </div>
        <div class="message-content ml-3 p-3 bg-blue-50 rounded-lg">
          <p>{{ message.content }}</p>
        </div>
      </div>
    </div>
    
    <!-- 助手消息 -->
    <div v-else-if="message.type === 'assistant'" class="assistant-message">
      <div class="flex items-start">
        <div class="assistant-avatar">
          <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white">
            <span>A</span>
          </div>
        </div>
        <div class="message-content ml-3 p-3 bg-white border border-gray-200 rounded-lg">
          <div v-html="formatMessage(message.content)"></div>
        </div>
      </div>
    </div>
    
    <!-- 工具调用开始 -->
    <div v-else-if="message.type === 'tool_start'" class="tool-message">
      <div class="flex items-start">
        <div class="tool-avatar">
          <div class="w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-white">
            <span>T</span>
          </div>
        </div>
        <div class="message-content ml-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div class="text-sm  mb-1">执行工具: {{ message.metadata?.function }}</div>
          
          <!-- 代码执行工具 -->
          <!-- <div v-if="message.metadata?.function === 'exec_code'" class="markdown-body"
           v-html="fotmatCode(message.metadata?.arguments?.code)">

          </div> -->
          
          <!-- 读取目录工具 -->
          <div v-if="message.metadata?.function === 'read_directory'" class="directory-info">
            <div class="markdown-body p-3 bg-white border border-gray-200 rounded-md">
              <p class="text-sm  mb-2">📂 正在读取目录：</p>
              <p class="font-mono text-blue-600 bg-gray-50 px-2 py-1 rounded inline-block">
                {{ message.metadata?.arguments?.path || '/' }}
              </p>
            </div>
          </div>
          
          <!-- 读取文件工具 -->
          <div v-else-if="message.metadata?.function === 'read_files'" class="file-info">
            <div class="markdown-body p-3 bg-white border border-gray-200 rounded-md">
              <p class="text-sm  mb-2">📁 正在读取文件：</p>
              <ul class="list-disc pl-6 space-y-1">
                <li v-for="file in message.metadata?.arguments?.filenames" 
                    :key="file"
                    class="font-mono text-green-600 hover:text-green-700 transition-colors">
                  {{ file }}
                </li>
                <li v-if="!message.metadata?.arguments?.filenames?.length" class="text-gray-400">
                  未指定文件
                </li>
              </ul>
            </div>
          </div>
          <!-- <div class="markdown-body text-sm flex justify-between items-center">
            <span>文件列表</span>
            ,<div v-html="formatFileList(message.metadata?.arguments?.filenames)"/>
          </div> -->
          
        </div>
      </div>
    </div>
    
    <!-- 代码执行开始 -->
    <div v-else-if="message.type === 'code_execution_start'" class="code-execution-message">
      <div class="flex items-start">
        <div class="code-avatar">
          <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white">
            <span>C</span>
          </div>
        </div>
        <div class="message-content ml-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div class="text-sm mb-1">代码执行:</div>
          
          <!-- 使用整合的代码执行组件 -->
          <code-execution
            :execution-id="message.metadata.execution_id"
            :code="message.metadata.code"
            :status="useCodeExecutionStore().executionStatus[message.metadata.execution_id]?.status"
            :outputs="useCodeExecutionStore().executionStatus[message.metadata.execution_id]?.output || []"
            :images="useCodeExecutionStore().executionStatus[message.metadata.execution_id]?.images || []"
            :error="useCodeExecutionStore().executionStatus[message.metadata.execution_id]?.error"
            @cancel="cancelExecution"
          />
        </div>
      </div>
    </div>
    
    <!-- 工具调用结果 -->
    <div v-else-if="message.type === 'tool_result'&&message.metadata.function!='exec_code'" class="tool-result">
      <div class="flex items-start">
        <div class="tool-avatar">
          <div class="w-8 h-8 rounded-full bg-gray-500 flex items-center justify-center text-white">
            <span>R</span>
          </div>
        </div>
        <div class="message-content ml-3 p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <div class="text-sm text-gray-500 mb-1">工具执行结果:</div>
          
          
          <div v-if="message.metadata?.function==='read_directory'" class="tool-other-result">
            <div v-if="message.metadata?.result?.status === 'success'" class="bg-green-50 p-2 rounded-md text-green-600">
            <p>目录读取成功</p>
          </div>
          <div v-else class="bg-red-50 p-2 rounded-md text-red-500">
            <p>目录读取失败:{{message.metadata?.result?.message}}</p>
          </div>
          </div>
          
          <!-- 文件读取结果 -->
          <div v-else class="tool-other-result">
            <div v-for="r in message.metadata.result" :key="r" class="text-sm">
              <div v-if="r.status === 'success'" class="p-2 rounded-md text-green-600">
                {{ `文件${r.content.path}读取成功` }}
              </div>
              <div v-else class="p-2 rounded-md text-red-500">
                {{ `文件读取失败: ${r.message}` }}
              </div>
            
          </div>
        </div>
      </div>
    </div>
  </div>
  </div>

</template>

<script setup lang="ts">
import { defineProps } from 'vue'
import type { Message } from '../../stores/conversation'
import { renderMarkdown } from '../../utils/markdown'
import { websocketService } from '../../services/websocket'
import { useCodeExecutionStore } from '../../stores/codeExecution'
import CodeExecution from './CodeExecution.vue'

const props = defineProps({
  message: {
    type: Object as () => Message,
    required: true
  }
})

// 格式化消息内容，支持Markdown
function formatMessage(content: string): string {
  try {
    return renderMarkdown(content)
  } catch (error) {
    // 如果markdown-it渲染失败，使用简单实现作为备选
    console.error('Markdown rendering failed:', error)
    return content
  }
}

// 取消代码执行
function cancelExecution(executionId: string) {
  websocketService.socket?.send(JSON.stringify({
    type: 'cancel_execution',
    data: { execution_id: executionId }
  }))
}
function fotmatCode(code:string):string{
  console.log("原始代码为：",code)
  code="```python"+"\n"+code+"\n"+"```"
  const result=formatMessage(code)
  console.log("格式化后的代码为：",result)
  return result
}

function formatFileList(filenames: string[] | undefined): string {
  if (!filenames || filenames.length === 0) {
    return '未指定文件'
  }
  return filenames.map(f => `- ${f}`).join('\n')
}

</script>

<style scoped>
.message-content {
  max-width: 48rem; /* 等效于 max-w-3xl */
}
</style>