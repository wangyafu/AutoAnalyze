import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useWorkspaceStore = defineStore('workspace', () => {
  const currentWorkspace = ref<string | null>(null)
  
  function setWorkspace(path: string) {
    currentWorkspace.value = path
  }
  
  function clearWorkspace() {
    currentWorkspace.value = null
  }
  
  return {
    currentWorkspace,
    setWorkspace,
    clearWorkspace
  }
})