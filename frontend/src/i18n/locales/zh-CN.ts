export default {
 
  home: {
    title: '欢迎使用 AutoAnalyze',
    subtitle: '智能数据分析助手，帮助您更高效地理解和处理数据',
    systemStatus: {
      backendService: '后端服务',
      connected: '已连接',
      connectionFailed: '连接失败',
      modelStatus: '模型状态',
      normal: '正常',
      abnormal: '异常',
      goToSettings: '前往设置',
      modifyConfig: '修改配置'
    },
    workspace: {
      title: '选择工作目录',
      description: '请输入要分析的项目目录完整路径：',
      placeholder: '例如：D:\\project\\data',
      confirm: '确认',
      current: '当前工作目录',
      enterWorkspace: '进入工作区'
    },
    features: {
      title: '功能亮点',
      naturalLanguage: {
        title: '自然语言交互',
        description: '通过自然语言描述需求，AI会自动编写Python代码并执行，无需编程知识'
      },
      dataVisualization: {
        title: '数据可视化',
        description: '支持显示图像输出，生成专业水准的图表和可视化效果'
      },
      toolCalls: {
        title: '实时工具调用',
        description: '实时查看AI对工具的调用情况，透明化分析过程'
      },
      customModel: {
        title: '自定义模型',
        description: '支持配置不同的大模型，包括双智能体模式和视觉模型'
      }
    }
  },
  settings: {
    title: '系统设置',
    server: {
      title: '服务器配置',
      port: '后端服务端口',
      portPlaceholder: '请输入端口号'
    },
    model: {
      main: '主模型配置',
      user: '用户代理模型配置',
      vision: '视觉模型配置'
    },
    button: {
      cancel: '取消',
      save: '保存设置'
    },
    message: {
      loading: '正在加载配置...',
      loadSuccess: '配置加载完成',
      loadFailed: '配置加载失败',
      saveSuccess: '设置已保存',
      saveFailed: '保存设置失败',
      portChanged: '设置已保存，正在应用新端口...',
      mainModelRequired: '请完整填写主模型配置，这是必需的',
      userModelIncomplete: '用户代理模型配置不完整，系统将无法使用双智能体模式',
      visionModelIncomplete: '视觉模型配置不完整，AI将无法理解生成的图片'
    }
  },
  // ... 现有内容保持不变 ...
  workspace: {
    fileExplorer: {
      title: '文件浏览器',
    },
    chat: {
      title: '数据分析助手',
      agent: {
        dual: '双智能体模式',
        single: '单智能体模式',
        switchMessage: '已切换到{mode}智能体模式'
      },
      buttons: {
        clearHistory: '清空会话',
        returnHome: '返回首页'
      }
    },
    messages: {
      selectWorkspace: '请先选择工作目录',
      clearConfirm: '确定要清空当前会话历史吗？此操作不可恢复。',
      clearSuccess: '会话已清空',
      clearFailed: '清空会话失败',
      warning: '警告',
      confirm: '确定',
      cancel: '取消'
    }
  }
}