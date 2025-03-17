<template>
  <div class="flex flex-col h-full bg-white">
    <div class="flex justify-between items-center px-4 py-3 bg-gray-100 border-b border-gray-200">
      <h3 class="text-lg font-medium">{{ figure ? figure.title : '图表查看器' }}</h3>
      <div class="flex gap-2">
        <el-button
          v-if="figure"
          @click="downloadFigure"
          type="primary"
          size="small"
          plain
        >
          <template #icon>
            <el-icon><Download /></el-icon>
          </template>
          下载
        </el-button>
        <el-button
          @click="$emit('close')"
          type="danger"
          size="small"
          circle
          :icon="Close"
        />
      </div>
    </div>
    
    <div v-if="!figure" class="no-figure">
      <p>没有图表数据</p>
    </div>
    
    <div v-else class="figure-container">
      <img 
        v-if="figure.format === 'image' || figure.format === 'png'" 
        :src="figureDataUrl" 
        :alt="figure.title" 
        class="figure-image"
      />
      
      <div v-else class="unsupported-format">
        <p>不支持的图表格式: {{ figure.format }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Download, Close } from '@element-plus/icons-vue';
import type{ Figure } from '../../types/api';

// Props
const props = defineProps<{
  figure?: Figure;
}>();

// Emits
const emit = defineEmits<{
  (e: 'close'): void;
}>();

// Computed
const figureDataUrl = computed(() => {
  if (props.figure) {
    return `data:image/png;base64,${props.figure.data}`;
  }
  return '';
});

// Methods
const downloadFigure = () => {
  if (!props.figure) return;
  
  const link = document.createElement('a');
  link.href = figureDataUrl.value;
  link.download = `${props.figure.title || 'figure'}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
</script>

