<template>
  <div class="code-execution">
    <!-- 代码显示部分 -->
    <div class="code-section mb-3">
      <div class="text-xs text-gray-500 mb-1">代码:</div>
      <div class="markdown-body" v-html="formattedCode"></div>
    </div>
    
    <!-- 执行状态和结果部分 -->
    <div class="result-section">
      <!-- 执行状态 -->
      <div class="mb-2 flex items-center">
        <div v-if="status === 'running'" 
             class="text-blue-500 flex items-center">
          <div class="animate-spin mr-2 h-4 w-4 border-2 border-blue-500 rounded-full border-t-transparent"></div>
          正在执行...
        </div>
        <div v-else-if="status === 'completed'"
             class="text-green-500 flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          执行完成
        </div>
        <div v-else-if="status === 'error'"
             class="text-red-500 flex items-center">
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
          执行错误
        </div>
        <button v-if="status === 'running'"
                @click="cancelExecution"
                class="ml-auto px-2 py-1 text-sm text-red-500 hover:text-red-600 border border-red-500 hover:border-red-600 rounded">
          终止执行
        </button>
      </div>
      
      <!-- 输出内容 -->
      <div v-if="outputs.length > 0" 
           class="bg-gray-100 p-2 rounded-md">
        <div v-for="(output, index) in outputs" 
             :key="index" class="mb-2">
          <div class="text-xs text-gray-500 mb-1">{{ output.type === 'stderr' ? '标准错误' : '标准输出' }}:</div>
          <pre class="bg-white p-2 rounded border text-sm overflow-x-auto" 
               :class="{'text-red-500': output.type === 'stderr'}">{{ output.content }}</pre>
        </div>
      </div>
      
      <!-- 图片输出 -->
      <div v-if="images.length > 0"
           class="mt-2 grid grid-cols-1 gap-2">
        <div v-for="(image, index) in images"
             :key="index" class="border rounded-lg overflow-hidden">
          <img :src="`data:image/${image.format};base64,${image.data}`" 
               class="w-full h-auto" alt="执行结果图片" />
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div v-if="error"
           class="mt-2 bg-red-50 p-2 rounded-md text-red-500">
        <p>{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits, computed } from 'vue'
import { useCodeExecutionStore } from '../../stores/codeExecution'
import { websocketService } from '../../services/websocket'
import { renderMarkdown } from '../../utils/markdown'

interface OutputItem {
  type: string;
  content: string;
}

interface ImageItem {
  type: string;
  format: string;
  data: string;
}

const props = defineProps({
  executionId: {
    type: String,
    required: true
  },
  code: {
    type: String,
    required: true
  },
  status: {
    type: String,
    default: 'running'
  },
  outputs: {
    type: Array as () => OutputItem[],
    default: () => []
  },
  images: {
    type: Array as () => ImageItem[],
    default: () => []
  },
  error: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['cancel'])

// 格式化代码，使用markdown渲染
const formattedCode = computed(() => {
  const codeWithMarkdown = '```python\n' + props.code + '\n```'
  return renderMarkdown(codeWithMarkdown)
})

function cancelExecution() {
  // 使用codeExecutionStore取消执行
  const codeExecutionStore = useCodeExecutionStore()
  codeExecutionStore.cancelExecution(props.executionId)
  
  // 通过websocket发送取消请求
  websocketService.socket?.send(JSON.stringify({
    type: 'cancel_execution',
    data: { execution_id: props.executionId }
  }))
  
  emit('cancel', props.executionId)
}
</script>

<style scoped>
.code-execution {
  width: 100%;
}

.code-section {
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.75rem;
}
</style>