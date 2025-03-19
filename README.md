## 简介
AutoAnalyze是一个让AI为你进行数据分析和处理的工具。你需要输入数据所在文件夹的路径，然后向AI用自然语言描述你的需求，然后AI就会根据你的需求读取文件、编写python代码并执行。


> :warning: 本项目仍处于早期阶段，目前正在**积极开发中**。
### Demo
| ![](assets/demo1.png) | ![](assets/demo2.png) |



## 功能亮点
- 通过自然语言描述需求，AI会自动编写Python代码并执行
- 你可以实时看到AI对工具的调用情况
- 自定义使用的大模型(需要与openai库兼容且支持Function Call)

## 安装
```shell
git clone https://github.com/wangyafu/AutoAnalyze
cd AutoAnalyze
```

## 快速开始
本项目采用前后端分离架构，前端使用Vue.js，后端使用FastAPI。因此你需要分别启动前后端服务。

在使用本项目之前，你需要确保已经具有Node.js和Python环境。另外本项目采用[uv](https://docs.astral.sh/uv/)作为Python环境的依赖管理工具。

### 启动前端
```shell
cd frontend
npm install
npm run dev
```

### 启动后端
```shell
cd backend
uv sync
uv run app/main.py
```