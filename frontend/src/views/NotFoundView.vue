<template>
  <div class="flex flex-col items-center justify-center min-h-screen p-6 text-center">
    <h1 class="text-6xl font-bold text-gray-800 mb-4">404</h1>
    <p class="text-xl mb-8">页面不存在</p>
    <el-button type="primary" @click="router.push('/')">返回首页</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>