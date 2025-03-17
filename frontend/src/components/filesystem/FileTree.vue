<template>
  <div class="file-tree">
    <el-tree
      :data="treeData"
      :props="defaultProps"
      @node-click="handleNodeClick"
      node-key="path"
      :expand-on-click-node="false"
      :default-expanded-keys="expanded"
    >
      <template #default="{ node, data }">
        <div class="custom-tree-node">
          <el-icon class="mr-1">
            <Folder v-if="data.type === 'directory'" />
            <Document v-else />
          </el-icon>
          <span>{{ node.label }}</span>
        </div>
      </template>
    </el-tree>
  </div>
</template>

<script setup lang="ts">

import type { FileItem } from '../../types/filesystem';
import { Document, Folder } from '@element-plus/icons-vue';

// Props
const props = defineProps<{
  items: FileItem[];
  expanded: string[];
}>();

// Emits
const emit = defineEmits<{
  (e: 'node-click', item: FileItem): void;
  (e: 'node-toggle', path: string): void;
}>();

// 配置
const defaultProps = {
  children: 'children',
  label: 'name',
};

// 转换数据结构
const treeData = computed(() => {
  const transformNode = (item: FileItem): any => {
    return {
      ...item,
      path: item.name,
      children: item.children?.map(transformNode)
    };
  };
  return props.items.map(transformNode);
});

// Methods
const handleNodeClick = (data: any) => {
  emit('node-click', data);
};
</script>

<style scoped>
.file-tree {
  font-size: 0.9rem;
  padding: 0.5rem;
}


@keyframes slide-down {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-up {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

.custom-tree-node {
  display: flex;
  align-items: center;
  font-size: 0.9rem;
}
</style>