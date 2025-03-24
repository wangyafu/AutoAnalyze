<template>
  <el-dialog
    v-model="visible"
    :title="file?.path"
    width="60%"
    destroy-on-close
    @closed="onClose"
  >
    <!-- 文本文件预览 -->
    <pre v-if="file?.preview_type === 'text'" class="whitespace-pre-wrap break-words">{{ file?.content }}</pre>
    
    <!-- 图片预览 -->
    <div v-else-if="file?.preview_type === 'image'" class="text-center">
      <img v-if="file?.base64_data" :src="`data:image/${getImageType(file.name)};base64,${file.base64_data}`" class="max-w-full max-h-[70vh]" />
      <p v-else class="text-gray-500">无法预览图片</p>
    </div>
    
    <!-- Excel/CSV预览 -->
    <div v-else-if="['excel', 'csv'].includes(file?.preview_type || '')" class="overflow-x-auto">
      <table v-if="file?.structured_data" class="min-w-full border-collapse border border-gray-300">
        <thead>
          <tr>
            <th v-for="(column, index) in file.structured_data.columns" :key="index" class="border border-gray-300 px-4 py-2 bg-gray-100">
              {{ column }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in file.structured_data.data" :key="rowIndex">
            <td v-for="(cell, cellIndex) in row" :key="cellIndex" class="border border-gray-300 px-4 py-2">
              {{ cell }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-gray-500">无法预览表格数据</p>
    </div>
    
    <!-- Word/PPT文档预览 -->
    <div v-else-if="file?.preview_type === 'markdown'" class="document-preview">
      <div v-if="file?.markdown_content" v-html="renderDocumentContent(file)" class="markdown-body"></div>
      <p v-else class="text-gray-500">无法预览文档内容</p>
      <div v-if="file?.is_truncated" class="text-gray-500 mt-4 text-center">
        [文档内容过长，仅显示部分内容]
      </div>
    </div>
    
    <!-- 其他文件类型 -->
    <div v-else class="text-center text-gray-500">
      <p>{{ file?.content || '无法预览此类型文件' }}</p>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch, defineProps, defineEmits } from 'vue'
import type { FilePreview } from '../../types'
import { renderDocumentPreview } from '../../utils/markdown'

const props = defineProps<{
  modelValue: boolean,
  file: FilePreview | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const visible = ref(props.modelValue)

// 监听props变化
watch(() => props.modelValue, (newVal) => {
  visible.value = newVal
})

// 监听内部状态变化
watch(() => visible.value, (newVal) => {
  emit('update:modelValue', newVal)
})

// 对话框关闭时触发
function onClose() {
  emit('update:modelValue', false)
}

// 根据文件名获取图片类型
function getImageType(filename: string): string {
  if (!filename) return 'png'
  const extension = filename.split('.').pop()?.toLowerCase() || ''
  
  switch (extension) {
    case 'jpg':
    case 'jpeg':
      return 'jpeg'
    case 'png':
      return 'png'
    case 'gif':
      return 'gif'
    case 'svg':
      return 'svg+xml'
    case 'webp':
      return 'webp'
    default:
      return 'png'
  }
}

// 渲染文档内容
function renderDocumentContent(file: FilePreview): string {
  if (!file.markdown_content) return ''
  
  return renderDocumentPreview(file.markdown_content, file.document_metadata)
}
</script>

<style scoped>
/* 添加文档预览样式 */
.document-preview {
  max-height: 70vh;
  overflow-y: auto;
  padding: 1rem;
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
  line-height: 1.6;
}

.document-meta {
  margin-bottom: 2rem;
}

.document-meta h1 {
  font-size: 1.8rem;
  margin-bottom: 0.5rem;
}

.meta-item {
  color: #666;
  font-size: 0.9rem;
}

.document-meta hr {
  margin: 1rem 0;
  border: 0;
  border-top: 1px solid #eee;
}
</style>