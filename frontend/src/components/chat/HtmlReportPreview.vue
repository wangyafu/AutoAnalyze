<template>
  <el-dialog
    v-model="dialogVisible"
    :title="$t('chat.htmlReport.title')"
    width="80%"
    destroy-on-close
    class="html-report-dialog"
    @closed="onDialogClosed"
  >
    <div class="flex justify-end mb-4 space-x-2">
      <el-button type="primary" size="small" @click="saveAsHtml">
        <i class="el-icon-download mr-1"></i>{{ $t('chat.htmlReport.saveAsHtml') }}
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
import { useI18n } from 'vue-i18n'  // 添加这行
import { ElMessage } from 'element-plus'

const { t } = useI18n()  // 添加这行

const props = defineProps({
  htmlContent: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])
const dialogVisible = ref(true)
const previewFrame = ref<HTMLIFrameElement | null>(null)

function handleClose() {
  emit('close')
}

async function saveAsHtml() {
  try {
    const blob = new Blob([props.htmlContent], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${t('chat.htmlReport.filename')}_${new Date().toISOString().slice(0, 10)}.html`
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success(t('chat.htmlReport.saveSuccess'))
  } catch (error) {
    console.error(t('chat.htmlReport.saveFailed'), error)
    ElMessage.error(t('chat.htmlReport.saveFailed'))
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