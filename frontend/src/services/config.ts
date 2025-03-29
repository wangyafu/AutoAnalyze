import { ref } from 'vue'

export const configService = {
  backendPort: ref(Number(localStorage.getItem('backendPort')) || 8000),
  language: ref(localStorage.getItem('language') || 'zh-CN'),
  

  setBackendPort(port: number) {
    if (this.backendPort.value !== port) {
      this.backendPort.value = port
      localStorage.setItem('backendPort', String(port))
    }
  },
  
  setLanguage(lang: string) {
    if (this.language.value !== lang) {
      this.language.value = lang
      localStorage.setItem('language', lang)
    }
  },
  
  getBackendBaseUrl() {
    return `http://127.0.0.1:${this.backendPort.value}`
  },
  
  getWebsocketUrl() {
    return `ws://127.0.0.1:${this.backendPort.value}/ws`
  }
}