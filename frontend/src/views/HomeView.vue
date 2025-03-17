<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <el-card class="w-full max-w-md">
      <div class="text-center">
        <h1 class="text-4xl font-bold text-gray-900 mb-4">DeepAnalyze</h1>
        <p class="text-lg text-gray-600 mb-8">让大模型为你进行数据分析</p>
        
        <div class="flex justify-center space-x-4">
          <el-button type="primary" size="large" @click="goToWorkspace">开始分析</el-button>
          <el-button size="large" @click="goToSettings">设置</el-button>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToWorkspace = () => {
  router.push('/workspace');
};

const goToSettings = () => {
  router.push('/settings');
};
</script>

<style scoped>
/* Element Plus 样式覆盖 */
:deep(.el-card) {
  border: none;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

:deep(.el-button) {
  font-weight: 500;
}

:deep(.el-button--primary) {
  background-color: #3498db;
  border-color: #3498db;
}

:deep(.el-button--primary:hover) {
  background-color: #2980b9;
  border-color: #2980b9;
}
</style>