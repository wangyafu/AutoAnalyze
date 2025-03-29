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
      modifyConfig: '修改配置',
      backendRestarted: '后端服务已重启',
      statusFailed: '获取系统状态失败'
    },
    workspace: {
      title: '选择工作目录',
      description: '请输入要分析的项目目录完整路径：',
      placeholder: '例如：D:\\project\\data',
      confirm: '确认',
      current: '当前工作目录',
      enterWorkspace: '进入工作区',
      quoteRemoved: '路径两端的引号已被自动移除'
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
    },
    settings: {
      // ... 其他内容保持不变 ...
      modelConfig: {
        type: '模型类型',
        apiKey: 'API密钥',
        apiKeyPlaceholder: '请输入API密钥',
        endpoint: 'API端点',
        endpointPlaceholder: 'https://api.openai.com/v1',
        modelName: '模型名称',
        modelNamePlaceholder: 'gpt-4'
      }
    }

  },
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
  },
  chat: {
    message: {
      user: '用户',
      assistant: '助手',
      tool: '工具',
      result: '结果',
      codeExecution: '代码执行',
      markdownError: 'Markdown渲染失败',
      noMessageElement: '无法找到消息元素',
      htmlBlockCount: '提取到的HTML代码块数量',
      runHtml: '运行HTML',
      directory: {
        reading: '正在读取目录',
        path: '目录路径'
      },
      file: {
        reading: '正在读取文件'
      },
      package: {
        installing: '正在安装包'
      }
    },
    tool: {
      executing: '执行工具',
      readingDirectory: '正在读取目录',
      readingFiles: '正在读取文件',
      noFiles: '未指定文件',
      installingPackage: '正在安装包',
      executionResult: '工具执行结果',
      directorySuccess: '目录读取成功',
      directoryFailed: '目录读取失败',
      fileSuccess: '文件{path}读取成功',
      fileFailed: '文件读取失败'
    },
    codeExecution: {
      executing: '正在执行...',
      completed: '执行完成',
      error: '执行错误',
      terminate: '终止执行',
      stderr: '标准错误',
      stdout: '标准输出'
    },
    htmlReport: {
      title: 'HTML数据分析报告',
      saveAsHtml: '保存为HTML文件',
      saveSuccess: 'HTML文件保存成功',
      saveFailed: '保存HTML文件失败',
      filename: '数据分析报告'
    },
    input: {
      placeholder: '输入您的问题或指令...',
      sendHint: '按 Ctrl+Enter 发送',
      send: '发送'
    }
  },
  message: {
    success: '操作成功',
    error: '操作失败',
    warning: '警告'
  }

}