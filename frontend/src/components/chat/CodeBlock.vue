<template>
  <div class="bg-gray-100 rounded-lg border border-gray-200 shadow-sm overflow-hidden transition-shadow hover:shadow-md my-3">
    <div class="flex justify-between items-center px-3 py-2 bg-gray-100 border-b border-gray-200">
      <el-tag
        v-if="language"
        size="small"
        type="info"
        class="uppercase"
      >{{ language }}</el-tag>
      <div class="flex gap-2">
        <el-button
          @click="copyCode"
          :type="copySuccess ? 'success' : 'primary'"
          size="small"
          plain
        >
          <template #icon>
            <el-icon><Document /></el-icon>
          </template>
          {{ copySuccess ? '已复制' : '复制' }}
        </el-button>
        <el-button
          @click="executeCode"
          type="success"
          size="small"
          plain
        >
          <template #icon>
            <el-icon><VideoPlay /></el-icon>
          </template>
          执行
        </el-button>
      </div>
    </div>
    
    <pre class="code-content"><code :class="`language-${language}`">{{ code }}</code></pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { Document, VideoPlay } from '@element-plus/icons-vue';

// Props
const props = defineProps<{
  code: string;
  language: string;
  id: string;
}>();

// Emits
const emit = defineEmits<{
  (e: 'execute', code: string, id: string): void;
  (e: 'copy', code: string): void;
}>();

// State
const copySuccess = ref(false);

// Methods
const executeCode = () => {
  emit('execute', props.code, props.id);
};

const copyCode = () => {
  emit('copy', props.code);
  copySuccess.value = true;
  
  // 重置复制状态
  setTimeout(() => {
    copySuccess.value = false;
  }, 2000);
};
</script>

