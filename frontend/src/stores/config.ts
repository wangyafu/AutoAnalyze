// 系统配置状态管理
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { SystemStatus, SystemConfig } from '../types/api';
import { getStatus, updateConfig as apiUpdateConfig } from '../api/config';

export const useConfigStore = defineStore('config', () => {
  // 状态
  const status = ref<SystemStatus | null>(null);
  const config = ref<SystemConfig | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // 计算属性
  const isConnected = computed(() => status.value?.status === 'running');
  const modelType = computed(() => config.value?.model.type || '');
  
  // 加载系统状态
  async function loadStatus() {
    loading.value = true;
    error.value = null;
    
    try {
      const statusData = await getStatus();
      status.value = statusData;
      return statusData;
    } catch (err) {
      console.error('加载系统状态失败:', err);
      error.value = '加载系统状态失败';
      return null;
    } finally {
      loading.value = false;
    }
  }
  
  // 更新系统配置
  async function updateConfig(configData: SystemConfig) {
    loading.value = true;
    error.value = null;
    
    try {
      await apiUpdateConfig(configData);
      config.value = configData;
      
      // 重新加载状态
      await loadStatus();
      
      return true;
    } catch (err) {
      console.error('更新系统配置失败:', err);
      error.value = '更新系统配置失败';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  return {
    // 状态
    status,
    config,
    loading,
    error,
    
    // 计算属性
    isConnected,
    modelType,
    
    // 方法
    loadStatus,
    updateConfig
  };
});