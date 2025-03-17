<template>
  <div class="text-file-viewer">
    <div class="viewer-header">
      <div class="file-info">
        <el-tag size="small" type="info" v-if="language">{{ language }}</el-tag>
        <span class="file-name">{{ fileName }}</span>
      </div>
      <el-button
        @click="copyContent"
        type="primary"
        size="small"
        plain
        :icon="copySuccess ? Check : Copy"
      >
        {{ copySuccess ? '已复制' : '复制' }}
      </el-button>
    </div>
    
    <el-scrollbar>
      <pre class="code-container"><code :class="`language-${language}`">{{ content }}</code></pre>
    </el-scrollbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Copy, Check } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// Props
const props = defineProps<{
  content: string;
  language?: string;
  fileName?: string;
}>();

// Emits
const emit = defineEmits<{
  (e: 'copy', content: string): void;
}>();

// State
const copySuccess = ref(false);

// Methods
const copyContent = () => {
  emit('copy', props.content);
  copySuccess.value = true;
  ElMessage.success('复制成功');
  
  // 重置复制状态
  setTimeout(() => {
    copySuccess.value = false;
  }, 2000);
};
</script>

<style scoped>
.text-file-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background-color: var(--el-bg-color-page);
  border-bottom: 1px solid var(--el-border-color-light);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-name {
  color: var(--el-text-color-primary);
  font-weight: 500;
}

.code-container {
  margin: 0;
  padding: 1rem;
  background-color: var(--el-bg-color);
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

code {
  font-family: inherit;
}

:deep(.el-button) {
  transition: all 0.3s;
  
  &:hover {
    transform: scale(1.05);
  }
}

:deep(.el-scrollbar) {
  flex: 1;
  height: 0;
}
</style>