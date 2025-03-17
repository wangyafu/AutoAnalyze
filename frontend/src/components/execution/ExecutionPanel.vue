<template>
  <div class="flex flex-col w-[350px] h-full overflow-hidden bg-white border-l border-gray-200">
    <div class="flex justify-between items-center px-4 py-3 border-b border-gray-200 bg-gray-100">
      <h3 class="text-lg font-medium">执行结果</h3>
      <el-tag
        :type="statusTagType"
        size="small"
        class="mx-2"
      >{{ statusText }}</el-tag>
      <div class="flex gap-2">
        <el-button
          v-if="isRunning"
          @click="$emit('cancel')"
          type="warning"
          size="small"
          plain
        >
          <template #icon>
            <el-icon><CircleClose /></el-icon>
          </template>
          取消
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
    
    <div class="execution-info">
      <div class="code-preview">
        <pre><code>{{ execution.code }}</code></pre>
      </div>
      
      <div v-if="execution.duration" class="execution-duration">
        执行时间: {{ formatDuration(execution.duration) }}
      </div>
    </div>
    
    <div class="outputs-container">
      <execution-output 
        v-for="output in execution.outputs" 
        :key="output.id" 
        :output="output"
        @view-figure="handleViewFigure"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { Close, CircleClose } from '@element-plus/icons-vue';
import type { Execution } from '../../types/execution';
import ExecutionOutput from './ExecutionOutput.vue';

// Props
const props = defineProps<{
  execution: Execution;
}>();

// Emits
const emit = defineEmits<{
  (e: 'cancel'): void;
  (e: 'close'): void;
  (e: 'view-figure', figureId: string): void;
}>();

// Computed
const isRunning = computed(() => {
  return props.execution.status === 'pending' || props.execution.status === 'running';
});

const statusTagType = computed(() => {
  switch (props.execution.status) {
    case 'pending': return 'info';
    case 'running': return 'primary';
    case 'completed': return 'success';
    case 'error': return 'danger';
    case 'cancelled': return '';
    default: return 'info';
  }
});

const statusText = computed(() => {
  switch (props.execution.status) {
    case 'pending': return '等待中';
    case 'running': return '执行中';
    case 'completed': return '已完成';
    case 'error': return '执行错误';
    case 'cancelled': return '已取消';
    default: return props.execution.status;
  }
});

// Methods
const formatDuration = (duration: number) => {
  if (duration < 1000) {
    return `${duration}ms`;
  } else {
    return `${(duration / 1000).toFixed(2)}s`;
  }
};

const handleViewFigure = (figureId: string) => {
  emit('view-figure', figureId);
};
</script>
