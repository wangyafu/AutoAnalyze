<template>
  <div class="file-explorer">
    <el-card class="explorer-card" :body-style="{ padding: '0' }">
      <template #header>
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium">文件浏览器</h3>
          <el-button-group>
            <el-button :icon="Refresh" circle @click="refreshCurrentDirectory" />
            <el-button :icon="FolderAdd" circle @click="createNewFolder" />
          </el-button-group>
        </div>
        <el-breadcrumb separator="/" class="mt-2">
          <el-breadcrumb-item @click="navigateToRoot" :class="{ 'cursor-pointer': true }">
            {{ rootPathName }}
          </el-breadcrumb-item>
          <el-breadcrumb-item 
            v-for="(segment, index) in pathSegments" 
            :key="index"
            @click="navigateToSegment(index)"
            :class="{ 'cursor-pointer': true }"
          >
            {{ segment }}
          </el-breadcrumb-item>
        </el-breadcrumb>
      </template>
      
      <el-scrollbar height="calc(100vh - 200px)">
        <div v-if="isLoading" class="flex justify-center items-center py-8">
          <el-spinner />
        </div>
        
        <div v-else-if="error" class="p-4">
          <el-alert :title="error" type="error" show-icon />
        </div>
        
        <div v-else class="file-tree-container">
          <file-tree 
            :items="items" 
            :expanded="expandedNodes"
            @node-click="handleNodeClick"
            @node-toggle="handleNodeToggle"
          />
        </div>
      </el-scrollbar>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import { useFileSystemStore } from '../../stores/filesystem';
import type{ FileItem } from '../../types/filesystem';
import FileTree from './FileTree.vue';
import { Refresh, FolderAdd } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// Props
const props = defineProps<{
  rootPath: string;
}>();

// Emits
const emit = defineEmits<{
  (e: 'file-select', file: FileItem): void;
  (e: 'directory-select', path: string): void;
}>();

// Store
const fileSystemStore = useFileSystemStore();

// State
const currentPath = ref(props.rootPath);
const expandedNodes = ref<string[]>([]);
const isLoading = computed(() => fileSystemStore.isLoading);
const error = computed(() => fileSystemStore.error);
const items = computed(() => fileSystemStore.files);

// Computed
const rootPathName = computed(() => {
  const parts = props.rootPath.split('/');
  return parts[parts.length - 1] || props.rootPath;
});

const pathSegments = computed(() => {
  if (!currentPath.value || currentPath.value === props.rootPath) return [];
  
  const relativePath = currentPath.value.slice(props.rootPath.length + 1);
  return relativePath.split('/');
});

// Methods
const navigateToRoot = async () => {
  await navigateTo(props.rootPath);
};

const refreshCurrentDirectory = async () => {
  try {
    await fileSystemStore.loadFiles(currentPath.value);
    ElMessage.success('刷新成功');
  } catch (err) {
    ElMessage.error('刷新失败');
  }
};

const createNewFolder = async () => {
  // TODO: 实现新建文件夹功能
  ElMessage.info('新建文件夹功能开发中...');
};

const navigateToSegment = async (index: number) => {
  const segments = pathSegments.value.slice(0, index + 1);
  const path = `${props.rootPath}/${segments.join('/')}`;
  await navigateTo(path);
};

const navigateTo = async (path: string) => {
  currentPath.value = path;
  await fileSystemStore.navigateTo(path);
  emit('directory-select', path);
};

const handleNodeClick = async (item: FileItem) => {
  if (item.type === 'directory') {
    const path = `${currentPath.value}/${item.name}`;
    await navigateTo(path);
  } else {
    emit('file-select', item);
    await fileSystemStore.getFilePreview(`${currentPath.value}/${item.name}`);
  }
};

const handleNodeToggle = (path: string) => {
  const index = expandedNodes.value.indexOf(path);
  if (index === -1) {
    expandedNodes.value.push(path);
  } else {
    expandedNodes.value.splice(index, 1);
  }
};

// Lifecycle
onMounted(async () => {
  if (props.rootPath) {
    await fileSystemStore.loadFiles(props.rootPath);
    currentPath.value = props.rootPath;
  }
});

// Watch for rootPath changes
watch(() => props.rootPath, async (newPath) => {
  if (newPath) {
    await fileSystemStore.loadFiles(newPath);
    currentPath.value = newPath;
    expandedNodes.value = [];
  }
});
</script>
