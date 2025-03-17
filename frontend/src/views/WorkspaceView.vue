<template>
  <div class="h-screen bg-gray-100 grid grid-cols-[250px_1fr_auto] overflow-hidden">
    <!-- 侧边栏：文件浏览器 -->
    <div class="bg-white border-r border-gray-200 flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 class="text-lg font-semibold text-gray-900">工作目录</h2>
        <el-button size="small" type="primary" @click="selectWorkspace">选择目录</el-button>
      </div>
      
      <div v-if="fileSystemStore.hasWorkspace" class="flex-1 overflow-y-auto p-4">
        <file-explorer 
          :root-path="fileSystemStore.workspace"
          @file-select="handleFileSelect"
          @directory-select="handleDirectorySelect"
        />
      </div>
      
      <div v-else class="flex-1 flex items-center justify-center text-gray-500">
        <el-empty description="请选择一个工作目录" />
      </div>
    </div>
    
    <!-- 主内容区：聊天窗口 -->
    <div class="flex flex-col overflow-hidden bg-white">
      <div v-if="!conversationStore.currentConversation" class="flex-1 flex flex-col items-center justify-center p-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">开始一个新对话</h2>
        <div class="flex gap-2 mb-8 w-full max-w-md">
          <el-input v-model="newConversationTitle" placeholder="输入对话标题" />
          <el-button type="primary" @click="createConversation">创建</el-button>
        </div>
        
        <div v-if="conversationStore.hasConversations" class="w-full max-w-md">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">历史对话</h3>
          <el-card v-for="conv in conversationStore.conversations" 
            :key="conv.id" 
            class="mb-2 cursor-pointer hover:shadow-md transition-shadow"
            @click="loadConversation(conv.id)"
          >
            <div class="text-gray-700">{{ conv.title }}</div>
          </el-card>
        </div>
      </div>
      
      <div v-else class="flex-1 flex flex-col overflow-hidden">
        <chat-window 
          :conversation="conversationStore.currentConversation"
          @send-message="handleSendMessage"
          @execute-code="handleExecuteCode"
          @close="handleCloseConversation"
        />
      </div>
    </div>
    
    <!-- 右侧面板：执行结果 -->
    <div v-if="executionStore.currentExecution" class="w-[350px] border-l border-gray-200 bg-gray-100 overflow-y-auto">
      <execution-panel 
        :execution="executionStore.currentExecution"
        @cancel="handleCancelExecution"
        @close="handleCloseExecution"
        @view-figure="handleViewFigure"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useFileSystemStore } from '../stores/filesystem';
import { useConversationStore } from '../stores/conversation';
import { useExecutionStore } from '../stores/execution';
import FileExplorer from '../components/filesystem/FileExplorer.vue';
import ChatWindow from '../components/chat/ChatWindow.vue';
import ExecutionPanel from '../components/execution/ExecutionPanel.vue';
import type { FileItem } from '../types/filesystem';

const router = useRouter();
const fileSystemStore = useFileSystemStore();
const conversationStore = useConversationStore();
const executionStore = useExecutionStore();

const newConversationTitle = ref('');

// 选择工作目录
const selectWorkspace = async () => {
  // 这里应该调用后端API来选择目录
  // 暂时使用模拟数据
  await fileSystemStore.setWorkspace('D:/example');
};

// 创建新对话
const createConversation = async () => {
  if (newConversationTitle.value.trim()) {
    await conversationStore.createConversation(newConversationTitle.value);
    newConversationTitle.value = '';
  }
};

// 加载对话
const loadConversation = async (id: string) => {
  await conversationStore.loadConversation(id);
};

// 文件操作相关方法
const handleFileSelect = async (file: FileItem) => {
  await fileSystemStore.getFilePreview(`${fileSystemStore.currentPath}/${file.name}`);
};

const handleDirectorySelect = (path: string) => {
  console.log('目录选择:', path);
};

// 对话相关方法
const handleSendMessage = (content: string) => {
  console.log('发送消息:', content);
};

const handleCloseConversation = () => {
  conversationStore.currentConversation = null;
};

// 代码执行相关方法
const handleExecuteCode = async (code: string, codeBlockId: string) => {
  if (!conversationStore.currentConversation) return;
  
  await executionStore.executeCode(
    conversationStore.currentConversation.id,
    code,
    codeBlockId
  );
};

const handleCancelExecution = () => {
  executionStore.cancelExecution();
};

const handleCloseExecution = () => {
  executionStore.currentExecution = null;
};

const handleViewFigure = (figureId: string) => {
  router.push(`/figure/${figureId}`);
};

onMounted(async () => {
  // 加载对话列表
  await conversationStore.loadConversations();
});
</script>

