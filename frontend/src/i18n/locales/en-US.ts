export default {
  home: {
    title: 'Welcome to AutoAnalyze',
    subtitle: 'Intelligent Data Analysis Assistant, helping you understand and process data more efficiently',
    systemStatus: {
      backendService: 'Backend Service',
      connected: 'Connected',
      connectionFailed: 'Connection Failed',
      modelStatus: 'Model Status',
      normal: 'Normal',
      abnormal: 'Abnormal',
      goToSettings: 'Go to Settings',
      modifyConfig: 'Modify Configuration'
    },
    workspace: {
      title: 'Select Working Directory',
      description: 'Please enter the full path of the project directory to analyze:',
      placeholder: 'Example: D:\\project\\data',
      confirm: 'Confirm',
      current: 'Current Working Directory',
      enterWorkspace: 'Enter Workspace',
      quoteRemoved: 'Quotes around the path have been automatically removed'
    },
    features: {
      title: 'Features',
      naturalLanguage: {
        title: 'Natural Language Interaction',
        description: 'AI automatically writes and executes Python code through natural language requirements, no programming knowledge required'
      },
      dataVisualization: {
        title: 'Data Visualization',
        description: 'Support image output, generate professional charts and visualization effects'
      },
      toolCalls: {
        title: 'Real-time Tool Calls',
        description: 'View AI tool calls in real-time, transparent analysis process'
      },
      customModel: {
        title: 'Custom Models',
        description: 'Support configuration of different large models, including dual-agent mode and vision models'
      }
    }
  },
  settings: {
    title: 'System Settings',
    server: {
      title: 'Server Configuration',
      port: 'Backend Service Port',
      portPlaceholder: 'Please enter port number'
    },
    model: {
      main: 'Main Model Configuration',
      user: 'User Agent Model Configuration',
      vision: 'Vision Model Configuration'
    },
    button: {
      cancel: 'Cancel',
      save: 'Save Settings'
    },
    message: {
      loading: 'Loading configuration...',
      loadSuccess: 'Configuration loaded',
      loadFailed: 'Failed to load configuration',
      saveSuccess: 'Settings saved',
      saveFailed: 'Failed to save settings',
      portChanged: 'Settings saved, applying new port...',
      mainModelRequired: 'Please complete the main model configuration, this is required',
      userModelIncomplete: 'User agent model configuration is incomplete, dual-agent mode will not be available',
      visionModelIncomplete: 'Vision model configuration is incomplete, AI will not be able to understand generated images'
    },
    modelConfig: {
      type: 'Model Type',
      apiKey: 'API Key',
      apiKeyPlaceholder: 'Please enter API key',
      endpoint: 'API Endpoint',
      endpointPlaceholder: 'https://api.openai.com/v1',
      modelName: 'Model Name',
      modelNamePlaceholder: 'gpt-4'
    }
  },
  workspace: {
    fileExplorer: {
      title: 'File Explorer',
    },
    chat: {
      title: 'Data Analysis Assistant',
      agent: {
        dual: 'Dual Agent Mode',
        single: 'Single Agent Mode',
        switchMessage: 'Switched to {mode} agent mode'
      },
      buttons: {
        clearHistory: 'Clear History',
        returnHome: 'Return Home'
      }
    },
    messages: {
      selectWorkspace: 'Please select a workspace first',
      clearConfirm: 'Are you sure you want to clear the current conversation history? This action cannot be undone.',
      clearSuccess: 'Conversation cleared',
      clearFailed: 'Failed to clear conversation',
      warning: 'Warning',
      confirm: 'Confirm',
      cancel: 'Cancel'
    }
  },
  chat: {
    message: {
      user: 'User',
      assistant: 'Assistant',
      tool: 'Tool',
      result: 'Result',
      codeExecution: 'Code Execution',
      markdownError: 'Markdown rendering failed',
      noMessageElement: 'Cannot find message element',
      htmlBlockCount: 'Number of HTML code blocks extracted',
      runHtml: 'Run HTML',
      directory: {
        reading: 'Reading Directory',
        path: 'Directory Path'
      },
      file: {
        reading: 'Reading Files'
      },
      package: {
        installing: 'Installing Package'
      }
    },
    tool: {
      executing: 'Executing Tool',
      readingDirectory: 'Reading Directory',
      readingFiles: 'Reading Files',
      noFiles: 'No files specified',
      installingPackage: 'Installing Package',
      executionResult: 'Tool Execution Result',
      directorySuccess: 'Directory read successfully',
      directoryFailed: 'Failed to read directory',
      fileSuccess: 'File {path} read successfully',
      fileFailed: 'Failed to read file'
    },
    codeExecution: {
      executing: 'Executing...',
      completed: 'Execution completed',
      error: 'Execution error',
      terminate: 'Terminate',
      stderr: 'Standard Error',
      stdout: 'Standard Output'
    },
    htmlReport: {
      title: 'HTML Data Analysis Report',
      saveAsHtml: 'Save as HTML file',
      saveSuccess: 'HTML file saved successfully',
      saveFailed: 'Failed to save HTML file',
      filename: 'Data Analysis Report'
    },
    input: {
      placeholder: 'Enter your question or command...',
      sendHint: 'Press Ctrl+Enter to send',
      send: 'Send'
    }
  },
  message: {
    success: 'Operation successful',
    error: 'Operation failed',
    warning: 'Warning'
  }
  
}