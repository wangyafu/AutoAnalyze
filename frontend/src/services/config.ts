import { ref } from 'vue'

export const configService = {
  backendPort: ref(Number(localStorage.getItem('backendPort')) || 8000),
  
  setBackendPort(port: number) {
    if (this.backendPort.value !== port) {
      this.backendPort.value = port
    }
  },
  
  getBackendBaseUrl() {
    return `http://127.0.0.1:${this.backendPort.value}`
  },
  
  getWebsocketUrl() {
    return `ws://127.0.0.1:${this.backendPort.value}/ws`
  }
}