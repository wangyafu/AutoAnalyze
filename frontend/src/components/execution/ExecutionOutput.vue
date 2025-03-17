<template>
  <div class="mb-3 rounded-lg border border-gray-200 overflow-hidden transition-shadow hover:shadow-sm" :class="outputClass">
    <!-- 标准输出或错误输出 -->
    <div v-if="isTextOutput" class="text-output">
      <div class="flex justify-between items-center px-3 py-2 text-sm border-b border-gray-200">
        <el-tag size="small" :type="output.type === 'error' ? 'danger' : 'info'">{{ outputTypeLabel }}</el-tag>
        <span class="text-gray-500 text-xs">{{ formatTime(output.timestamp) }}</span>
      </div>
      <pre class="p-3 whitespace-pre-wrap break-words font-mono text-sm leading-relaxed">{{ outputContent }}</pre>
    </div>
    
    <!-- 图表输出 -->
    <div v-else-if="isFigureOutput" class="figure-output">
      <div class="flex justify-between items-center px-3 py-2 bg-green-50 border-b border-gray-200">
        <el-tag size="small" type="success">图表: {{ figureTitle }}</el-tag>
        <el-button
          @click="viewFigure"
          type="primary"
          size="small"
          plain
        >
          <template #icon>
            <el-icon><View /></el-icon>
          </template>
          查看
        </el-button>
      </div>
      <div class="p-3 flex justify-center items-center cursor-pointer hover:bg-gray-100" @click="viewFigure">
        <img :src="figureDataUrl" :alt="figureTitle" class="max-w-full max-h-[300px] object-contain" />
      </div>
    </div>
    
    <!-- 其他类型输出 -->
    <div v-else class="unknown-output">
      <div class="flex justify-between items-center px-3 py-2 bg-gray-100 border-b border-gray-200">
        <el-tag size="small" type="info">{{ output.type }}</el-tag>
        <span class="text-gray-500 text-xs">{{ formatTime(output.timestamp) }}</span>
      </div>
      <div class="p-3 text-gray-500 text-sm">不支持的输出类型</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { View } from '@element-plus/icons-vue';
import type{ ExecutionOutput } from '../../types/execution';
import type{ Figure } from '../../types/api';

// Props
const props = defineProps<{
  output: ExecutionOutput;
}>();

// Emits
const emit = defineEmits<{
  (e: 'view-figure', figureId: string): void;
}>();

// Computed
const outputClass = computed(() => {
  return {
    'stdout-output': props.output.type === 'stdout',
    'stderr-output': props.output.type === 'stderr',
    'result-output': props.output.type === 'result',
    'error-output': props.output.type === 'error',
    'figure-output': props.output.type === 'figure'
  };
});

const outputTypeLabel = computed(() => {
  switch (props.output.type) {
    case 'stdout': return '标准输出';
    case 'stderr': return '标准错误';
    case 'result': return '执行结果';
    case 'error': return '执行错误';
    default: return props.output.type;
  }
});

const isTextOutput = computed(() => {
  return ['stdout', 'stderr', 'result', 'error'].includes(props.output.type);
});

const isFigureOutput = computed(() => {
  return props.output.type === 'figure';
});

const outputContent = computed(() => {
  if (isTextOutput.value) {
    return props.output.content as string;
  }
  return '';
});

const figure = computed(() => {
  if (isFigureOutput.value) {
    return props.output.content as Figure;
  }
  return null;
});

const figureTitle = computed(() => {
  return figure.value?.title || '未命名图表';
});

const figureDataUrl = computed(() => {
  if (figure.value) {
    return `data:image/png;base64,${figure.value.data}`;
  }
  return '';
});

// Methods
const formatTime = (timestamp: string) => {
  const date = new Date(timestamp);
  return date.toLocaleTimeString();
};

const viewFigure = () => {
  if (figure.value) {
    emit('view-figure', figure.value.figure_id);
  }
};
</script>

