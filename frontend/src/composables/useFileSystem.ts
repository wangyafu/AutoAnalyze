// 文件系统操作
import { computed } from 'vue';
import { useFileSystemStore } from '../stores/filesystem';

export function useFileSystem() {
  const fileSystemStore = useFileSystemStore();
  
  // 文件列表
  const files = computed(() => fileSystemStore.files);
  
  // 当前路径
  const currentPath = computed(() => fileSystemStore.currentPath);
  
  // 是否加载中
  const isLoading = computed(() => fileSystemStore.isLoading);
  
  // 设置工作目录
  const setWorkspace = async (path: string) => {
    return await fileSystemStore.setWorkspace(path);
  };
  
  // 导航到指定路径
  const navigateTo = async (path: string) => {
    await fileSystemStore.navigateTo(path);
  };
  
  // 刷新文件列表
  const refreshFiles = async () => {
    await fileSystemStore.refreshFiles();
  };
  
  // 获取文件预览
  const getFilePreview = async (path: string) => {
    return await fileSystemStore.getFilePreview(path);
  };
  
  // 获取文本文件内容
  const getTextFileContent = async (path: string) => {
    return await fileSystemStore.getTextFileContent(path);
  };
  
  return {
    files,
    currentPath,
    isLoading,
    setWorkspace,
    navigateTo,
    refreshFiles,
    getFilePreview,
    getTextFileContent
  };
}