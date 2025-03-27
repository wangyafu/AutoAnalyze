<template>
  <el-dialog
    v-model="dialogVisible"
    title="HTML数据分析报告"
    width="80%"
    destroy-on-close
    class="html-report-dialog"
    @closed="onDialogClosed"
  >
    <div class="flex justify-end mb-4 space-x-2">
      <el-button type="primary" size="small" @click="saveAsHtml">
        <i class="el-icon-download mr-1"></i>保存为HTML文件
      </el-button>
    </div>
    
    <div class="html-preview-container bg-white rounded-lg p-4 border" style="height: 70vh; overflow: auto;">
      <iframe
        ref="previewFrame"
        class="w-full h-full"
        sandbox="allow-scripts"
        :srcdoc="htmlContent"
      ></iframe>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  htmlContent: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])
const dialogVisible = ref(true)
const previewFrame = ref<HTMLIFrameElement | null>(null)

// 监听对话框关闭事件
function handleClose() {
  emit('close')
}

// 保存为HTML文件
async function saveAsHtml() {
  try {
    // 创建Blob对象
    const blob = new Blob([props.htmlContent], { type: 'text/html' })
    
    // 创建下载链接
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `数据分析报告_${new Date().toISOString().slice(0, 10)}.html`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('HTML文件保存成功')
  } catch (error) {
    console.error('保存HTML文件失败:', error)
    ElMessage.error('保存HTML文件失败')
  }
}

// 监听对话框关闭
function onDialogClosed() {
  dialogVisible.value = false
  handleClose()
}

// 监听对话框可见性变化
watch(dialogVisible, (newVal) => {
  if (!newVal) {
    onDialogClosed()
  }
})

// 生命周期钩子
onMounted(() => {
  // 可以在这里添加对iframe的额外处理
})

onBeforeUnmount(() => {
  // 清理资源
})
</script>

<style scoped>
.html-report-dialog :deep(.el-dialog__body) {
  padding: 10px 20px;
}
</style>