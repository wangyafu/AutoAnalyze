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
      enterWorkspace: 'Enter Workspace'
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
    }
  }
  
}