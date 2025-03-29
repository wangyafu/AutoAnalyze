import { ref } from 'vue'

// 国际化文本定义
export const i18nMessages = {
  'zh-CN': {
    filePreview: {
      binaryWarning: '二进制文件无法预览',
      previewFailed: '文件预览失败'
    },
    websocket: {
      connected: '已成功和服务器建立websocket连接',
      connectionClosed: 'WebSocket连接已关闭',
      error: 'WebSocket错误',
      parseError: '解析WebSocket消息失败',
      notConnected: 'WebSocket未连接，无法发送消息',
      replyCompleted: '智能体回复完毕',
      serverError: '服务器发生错误'
    }
  },
  'en-US': {
    filePreview: {
      binaryWarning: 'Binary file cannot be previewed',
      previewFailed: 'File preview failed'
    },
    websocket: {
      connected: 'WebSocket connection established successfully',
      connectionClosed: 'WebSocket connection closed',
      error: 'WebSocket error',
      parseError: 'Failed to parse WebSocket message',
      notConnected: 'WebSocket not connected, cannot send message',
      replyCompleted: 'AI agent reply completed',
      serverError: 'Server error occurred'
    }
  }
}

export const configService = {
  backendPort: ref(Number(localStorage.getItem('backendPort')) || 8000),
  language: ref(localStorage.getItem('language') || 'en-US'),
  

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
  },
  
  // 获取国际化文本
  t(key: string): string {
    const keys = key.split('.');
    let result = i18nMessages[this.language.value] || i18nMessages['zh-CN'];
    
    for (const k of keys) {
      if (result[k] === undefined) return key;
      result = result[k];
    }
    
    return result as string;
  }
}