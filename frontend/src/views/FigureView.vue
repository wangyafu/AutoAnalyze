<template>
  <div class="min-h-screen bg-gray-100 p-6">
    <el-card class="max-w-6xl mx-auto">
      <template #header>
        <div class="flex justify-between items-center">
          <h1 class="text-2xl font-bold text-gray-900">{{ figure ? figure.title : '图表查看' }}</h1>
          <el-button @click="goBack" icon="ArrowLeft">返回</el-button>
        </div>
      </template>

      <div class="min-h-[400px] flex items-center justify-center">
        <el-skeleton v-if="loading" :rows="10" animated />
        
        <el-alert
          v-else-if="error"
          :title="error"
          type="error"
          show-icon
          :closable="false"
          class="w-full"
        />
        
        <div v-else-if="figure" class="w-full">
          <figure-viewer :figure="figure" @close="goBack" />
        </div>
        
        <el-empty v-else description="未找到图表" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type{ Figure } from '../types/api';
import FigureViewer from '../components/execution/FigureViewer.vue';

const route = useRoute();
const router = useRouter();

const figureId = route.params.figureId as string;
const figure = ref<Figure | null>(null);
const loading = ref(true);
const error = ref<string | null>(null);

// 加载图表数据
const loadFigure = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    // 这里应该调用API获取图表数据
    // 暂时使用模拟数据
    setTimeout(() => {
      figure.value = {
        figure_id: figureId,
        title: '示例图表',
        format: 'image',
        data: '' // 这里应该是base64编码的图片数据
      };
      loading.value = false;
    }, 1000);
  } catch (err) {
    console.error('加载图表失败:', err);
    error.value = '加载图表失败';
    loading.value = false;
  }
};

// 返回上一页
const goBack = () => {
  router.back();
};

onMounted(() => {
  loadFigure();
});
</script>

<style scoped>

</style>