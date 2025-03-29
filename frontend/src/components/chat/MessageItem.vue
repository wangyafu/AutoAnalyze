<template>
  <div class="mb-4" :data-message-id="message.id" ref="messageRoot">
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
    <div v-else-if="(message.type === 'assistant') || (message.type==='user_assistant')" class="assistant-message">
      <div class="flex items-start">
        <div class="assistant-avatar" v-if="message.type==='assistant'">
          <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white">
            <span>A</span>
          </div>
        </div>
        <div class="assistant-avatar" v-else>
          <div class="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white">
            <span>P</span>
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
          <div class="text-sm mb-1">{{ $t('chat.tool.executing') }}: {{ message.metadata?.function }}</div>
          
          <!-- 读取目录工具 -->
          <div v-if="message.metadata?.function === 'read_directory'" class="directory-info">
            <div class="markdown-body p-3 bg-white border border-gray-200 rounded-md">
              <p class="text-sm mb-2">📂 {{ $t('chat.message.directory.reading') }}</p>
              <p class="font-mono text-blue-600 bg-gray-50 px-2 py-1 rounded inline-block">
                {{ message.metadata?.arguments?.path || $t('chat.message.directory.path') }}
              </p>
            </div>
          </div>
          
          <!-- 读取文件工具 -->
          <div v-else-if="message.metadata?.function === 'read_files'" class="file-info">
            <div class="markdown-body p-3 bg-white border border-gray-200 rounded-md">
              <p class="text-sm mb-2">📁 {{ $t('chat.message.file.reading') }}</p>
              <ul class="list-disc pl-6 space-y-1">
                <li v-for="file in message.metadata?.arguments?.filenames" 
                    :key="file"
                    class="font-mono text-green-600 hover:text-green-700 transition-colors">
                  {{ file }}
                </li>
                <li v-if="!message.metadata?.arguments?.filenames?.length" class="text-gray-400">
                  {{ $t('chat.tool.noFiles') }}
                </li>
              </ul>
            </div>
          </div>
          
          <!-- 安装包工具 -->
          <div v-else-if="message.metadata?.function === 'install_package'" class="package-info">
            <div class="markdown-body p-3 bg-white border border-gray-200 rounded-md">
              <p class="text-sm mb-2">📦 {{ $t('chat.message.package.installing') }}</p>
              <p class="font-mono text-purple-600 bg-gray-50 px-2 py-1 rounded inline-block">
                {{ message.metadata?.arguments?.package_name }}
              </p>
            </div>
          </div>
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
          <div class="text-sm mb-1">{{ $t('chat.message.codeExecution') }}:</div>
          
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
          <div class="text-sm text-gray-500 mb-1">{{ $t('chat.tool.executionResult') }}:</div>
          
          <div v-if="message.metadata?.function==='read_directory'" class="tool-other-result">
            <div v-if="message.metadata?.result?.status === 'success'" class="bg-green-50 p-2 rounded-md text-green-600">
              <p>{{ $t('chat.tool.directorySuccess') }}</p>
            </div>
            <div v-else class="bg-red-50 p-2 rounded-md text-red-500">
              <p>{{ $t('chat.tool.directoryFailed') }}: {{ message.metadata?.result?.message }}</p>
            </div>
          </div>
          
          <!-- 安装包结果 -->
          <div v-else-if="message.metadata?.function === 'install_package'" class="tool-other-result">
            <div v-if="message.metadata?.result?.status === 'success'" class="bg-green-50 p-2 rounded-md text-green-600">
              <p>{{ message.metadata?.result?.message }}</p>
            </div>
            <div v-else class="bg-red-50 p-2 rounded-md text-red-500">
              <p>{{ message.metadata?.result?.message }}</p>
              <p class="text-xs mt-1">{{ message.metadata?.result?.details }}</p>
            </div>
          </div>

          <!-- 文件读取结果 -->
          <div v-else class="tool-other-result">
            <div v-for="r in message.metadata.result" :key="r" class="text-sm">
              <div v-if="r.status === 'success'" class="p-2 rounded-md text-green-600">
                {{ $t('chat.tool.fileSuccess', { path: r.info.path }) }}
              </div>
              <div v-else class="p-2 rounded-md text-red-500">
                {{ $t('chat.tool.fileFailed') }}: {{ r.message }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <html-report-preview
    v-if="showHtmlPreview"
    :html-content="htmlContent"
    @close="showHtmlPreview = false"
  />
</template>

<script setup lang="ts">
import { defineProps, ref, computed, onMounted, watch } from 'vue'
import type { Message } from '../../stores/conversation'
import { renderMarkdown } from '../../utils/markdown'
import { websocketService } from '../../services/websocket'
import { useCodeExecutionStore } from '../../stores/codeExecution'
import CodeExecution from './CodeExecution.vue'
import HtmlReportPreview from './HtmlReportPreview.vue'
import { ElMessage } from 'element-plus'
import { nextTick } from 'vue'
import { useI18n } from 'vue-i18n'  // 添加这行
const { t } = useI18n()  // 添加这行
const props = defineProps({
  message: {
    type: Object as () => Message,
    required: true
  }
})

// 添加对根元素的引用
const messageRoot = ref<HTMLElement | null>(null)

// HTML报告预览相关变量
const showHtmlPreview = ref(false)
const htmlContent = ref('')
const htmlCodeBlocks = ref<Array<{id: number, code: string}>>([])

// 格式化消息内容，支持Markdown
function formatMessage(content: string): string {
  try {
    const formattedContent = renderMarkdown(content)
    
    // 在DOM更新后提取HTML代码块
    nextTick(() => {
      extractHtmlCodeBlocks()
    })
    
    return formattedContent
  } catch (error) {
    // 如果markdown-it渲染失败，使用简单实现作为备选
    console.error('Markdown rendering failed:', error)
    ElMessage.error(t('chat.message.markdownError'))
    return content
  }
}

// 提取HTML代码块
function extractHtmlCodeBlocks() {
  // 使用ref直接获取组件根元素
  const messageElement = messageRoot.value
  if (!messageElement) {
    console.warn('无法找到消息元素:', props.message.id)
    return
  }
  
  const codeBlocks = messageElement.querySelectorAll('pre code.language-html')
  console.log('提取到的HTML代码块数量:', codeBlocks.length)
  // 清空现有代码块
  htmlCodeBlocks.value = []
  
  // 提取代码块内容并添加运行按钮
  codeBlocks.forEach((codeBlock, index) => {
    // 存储代码块内容
    const codeContent = codeBlock.textContent || ''
    htmlCodeBlocks.value.push({
      id: index,
      code: codeContent
    })
    
    // 为代码块添加自定义属性，用于标识
    codeBlock.setAttribute('data-html-block-id', index.toString())
    
    // 添加运行按钮
    const preElement = codeBlock.parentElement
    if (preElement && !preElement.querySelector('.run-html-button')) {
      console.log("添加运行按钮")
      // 创建运行按钮
      const runButton = document.createElement('button')
      runButton.className = 'run-html-button absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600 transition-colors'
      // 修改相关文本
      runButton.textContent = t('chat.message.runHtml')
      runButton.onclick = () => runHtmlCode(codeContent)
      
      // 确保pre元素有相对定位
      preElement.style.position = 'relative'
      preElement.appendChild(runButton)
    }
  })
}

// 运行HTML代码
function runHtmlCode(code: string) {
  htmlContent.value = code
  showHtmlPreview.value = true
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