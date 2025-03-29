## Introduction

[中文版本请点击这里](https://github.com/wangyafu/AutoAnalyze/blob/master/README_CN.md)
AutoAnalyze is an AI-powered tool for automated data analysis and processing. Simply provide the path to your data directory and describe your requirements in natural language. The AI will then read files, write Python code, and execute it accordingly. You can monitor the AI's tool usage in real-time.

> :warning: This project is still in early stages and under active development.

### Support Us
If you find this project helpful, please consider supporting us by voting on ProductHunt:
[![ProductHunt](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=autoanalyze&theme=light)](https://www.producthunt.com/posts/autoanalyze)

### Demo

![Interface Display1](assets/demo1.png)
![Interface Display2](assets/demo2.png)

## Key Features

- Natural language processing for automated Python code generation
- Real-time monitoring of AI tool usage
- Customizable LLM configurations
- Support for image output display

## Installation

```shell
git clone https://github.com/wangyafu/AutoAnalyze
cd AutoAnalyze
```



## Quick Start

This project uses a frontend-backend separation architecture:

- Frontend: Vue.js
- Backend: FastAPI
Ensure you have Node.js and Python environments installed. We use uv for Python dependency management.

### Start Frontend

```shell
cd frontend
npm install
npm run dev
 ```

### Start Backend

```shell
cd backend
uv sync
uv run app/main.py
 ```

### Register IPython Kernel

To enable image output, real-time code execution monitoring, and code cancellation features (introduced in v0.02), register the IPython kernel:

```shell
# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate.bat  # cmd
.venv\Scripts\Activate.ps1  # PowerShell

where python # Should include project-specific paths

python -m ipykernel install --user
```

## Dual Agent Mode

This mode is still in testing. It introduces a user agent that is responsible for planning. The benefits are:

1. You can use LLMs that don't support Function Call capabilities. The user agent doesn't directly call tools but guides the tool-calling agent to complete tasks.
2. Complex tasks can be completed through collaboration between agents.
However, the current dual agent mode implementation is rudimentary and may not improve task completion rates.

## LLM Configuration

Modify backend/config.yaml or use the web interface to configure LLM settings. Currently supports OpenAI-compatible APIs with function call capability.

Tested models include qwen-plus, qwen-max, and deepseek-chat (deepseek-v3).

## Notes

- If you're using Windows, you'll need to open two command line windows to run the services. In the backend service command line window, you can see API request information. Logs will be recorded in backend/app.log. The frontend service will print received websocket messages and some error information in the console, which can help you debug issues.
- If the homepage shows "Backend Service: Connection Failed", it means the backend service has not started or failed to start.
- If the homepage shows "Backend Service: Connected, Model Status Abnormal", it means the backend service started successfully, but the model cannot be used normally. (The backend will send a request to the /models endpoint of your specified endpoint, and if the request fails, it is considered that the model cannot be used)
- Under normal circumstances, the homepage will display "Backend Service: Connected, Model Status Normal".
- By default, the backend service runs on port 8000, and the frontend service runs on port 5173. If you want to run services on other ports, you need to make corresponding modifications in backend/config.yaml and on the frontend interface.
- Most code is co-developed with DeepSeek-R1 and Claude. Project logo generated by Gemini 2.0 Flash Experimental. Special thanks to these AI collaborators for accelerating prototype development.