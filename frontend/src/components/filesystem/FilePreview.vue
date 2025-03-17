<template>
  <div class="file-preview">
    <el-card class="preview-card" :body-style="{ padding: '0' }">
      <template #header>
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium">{{ file ? file.name : '文件预览' }}</h3>
          <div class="flex gap-2">
            <el-button v-if="file" @click="$emit('open-external', file)" type="primary" size="small" plain>
              <template #icon><el-icon><Open /></el-icon></template>
              在外部打开
            </el-button>
            <el-button @click="$emit('close')" type="danger" size="small" circle :icon="Close" />
          </div>
        </div>
      </template>
    
    <div v-if="!file" class="flex justify-center items-center h-full">
        <el-empty description="请选择一个文件进行预览" />
      </div>
      
      <div v-else-if="loading" class="flex justify-center items-center h-full">
        <el-spinner />
      </div>
    
    <div v-else class="preview-content">
      <!-- 文本文件预览 -->
      <text-file-viewer 
        v-if="type === 'text'"
        :content="content!"
        :language="getLanguageByExtension(file.name)"
        :file-name="file.name"
        @copy="$emit('copy', content!)"
      />
      
      <!-- 图片预览 -->
      <div v-else-if="type === 'image'" class="image-preview">
        <img :src="content" :alt="file.name" />
      </div>
      
      <!-- 不支持的文件类型 -->
      <div v-else class="unsupported-file">
        <p>不支持预览此类型的文件</p>
        <p>文件类型: {{ file.extension || '未知' }}</p>
        <button @click="$emit('open-external', file)" class="external-btn">在外部打开</button>
      </div>
      
      <!-- 文件被截断提示 -->
      <!-- <div v-if="file.truncated" class="truncated-notice">
        <p>文件内容过大，仅显示部分内容</p>
        <button @click="$emit('open-external', file)" class="external-btn">在外部打开完整文件</button>
      </div> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue';
import { FileItem, FilePreview as FilePreviewType } from '../../types/filesystem';
import TextFileViewer from './TextFileViewer.vue';
import { getLanguageByExtension } from '../../utils/formatter';
import { Open, Close } from '@element-plus/icons-vue';

// Props
const props = defineProps<{
  file?: FileItem;
  content?: string;
  type?: 'text' | 'image' | 'other';
}>();

// Emits
const emit = defineEmits<{
  (e: 'close'): void;
  (e: 'open-external', file: FileItem): void;
  (e: 'copy', content: string): void;
}>();

// State
const loading = ref(false);

// Watch for file changes
watch(() => props.file, (newFile) => {
  if (newFile) {
    loading.value = true;
    // 模拟加载延迟
    setTimeout(() => {
      loading.value = false;
    }, 300);
  }
});
</script>

