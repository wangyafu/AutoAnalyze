// 文件系统状态管理
import { defineStore } from 'pinia';
import type { FileDirectory, FileItem, FilePreview, FileSystemEvent } from '../types/filesystem';
import { setWorkspace, getFiles, getFilePreview, getTextFileContent } from '../api/filesystem';
import { createWebSocketClient } from '../api/websocket';

export const useFileSystemStore = defineStore('filesystem', {
  state: () => ({
    workspace: '',
    currentPath: '',
    files: [] as FileItem[],
    selectedFile: null as FileItem | null,
    filePreview: null as FilePreview | null,
    isLoading: false,
    error: null as string | null
  }),
  
  getters: {
    hasWorkspace: (state) => !!state.workspace,
    currentDirectory: (state) => {
      return {
        path: state.currentPath || state.workspace,
        items: state.files
      } as FileDirectory;
    }
  },
  
  actions: {
    // 设置工作目录
    async setWorkspace(path: string) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await setWorkspace(path);
        this.workspace = response.workspace;
        this.currentPath = response.workspace;
        
        // 加载根目录文件
        await this.loadFiles();
        
        // 订阅文件系统变更
        this.subscribeToFileSystemChanges();
        
        return true;
      } catch (error) {
        console.error('设置工作目录失败:', error);
        this.error = '设置工作目录失败';
        return false;
      } finally {
        this.isLoading = false;
      }
    },
    
    // 加载文件列表
    async loadFiles(path?: string) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await getFiles(path);
        this.files = response.items;
        
        if (path) {
          this.currentPath = path;
        }
      } catch (error) {
        console.error('加载文件列表失败:', error);
        this.error = '加载文件列表失败';
      } finally {
        this.isLoading = false;
      }
    },
    
    // 导航到指定路径
    async navigateTo(path: string) {
      if (path === this.currentPath) return;
      
      await this.loadFiles(path);
    },
    
    // 获取文件预览
    async getFilePreview(path: string) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const preview = await getFilePreview(path);
        this.filePreview = preview;
        return preview;
      } catch (error) {
        console.error('获取文件预览失败:', error);
        this.error = '获取文件预览失败';
        return null;
      } finally {
        this.isLoading = false;
      }
    },
    
    // 获取文本文件内容
    async getTextFileContent(path: string) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await getTextFileContent(path);
        return response.content;
      } catch (error) {
        console.error('获取文件内容失败:', error);
        this.error = '获取文件内容失败';
        return null;
      } finally {
        this.isLoading = false;
      }
    },
    
    // 刷新文件列表
    async refreshFiles() {
      await this.loadFiles(this.currentPath);
    },
    
    // 订阅文件系统变更
    subscribeToFileSystemChanges() {
      const wsClient = createWebSocketClient();
      wsClient.connect();
      
      wsClient.subscribe('filesystem_change', (data: FileSystemEvent) => {
        this.handleFileSystemChange(data);
      });
    },
    
    // 处理文件系统变更
    handleFileSystemChange(event: FileSystemEvent) {
      // 根据事件类型处理文件系统变更
      switch (event.event) {
        case 'created':
        case 'modified':
        case 'deleted':
          // 如果变更发生在当前目录，刷新文件列表
          if (event.path.startsWith(this.currentPath)) {
            this.refreshFiles();
          }
          break;
      }
    }
  }
});