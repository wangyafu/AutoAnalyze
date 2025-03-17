import os
import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import sys
# 将 app 文件夹的路径添加到 sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from app.api.router import api_router
from app.websocket.router import router as websocket_router
from app.config import get_settings
from app.db.base import init_db
from app.services.model_service import initialize_model
from app.services.filesystem_service import start_file_watcher

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)

# 创建应用实例
app = FastAPI(
    title="DeepAnalyze",
    description="数据分析助手API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:{get_settings().server.frontend_port}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"未处理的异常: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": f"服务器错误: {str(exc)}"},
    )

# 挂载API路由
app.include_router(api_router, prefix="/api")

# 挂载WebSocket路由
app.include_router(websocket_router)

# 创建数据目录
data_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent / "data"
data_dir.mkdir(exist_ok=True)

# 确保utils目录存在
def ensure_utils_dir():
    """确保utils目录存在"""
    utils_dir = Path(os.path.dirname(os.path.abspath(__file__))) / "utils"
    utils_dir.mkdir(exist_ok=True)
    
    # 创建__init__.py
    init_file = utils_dir / "__init__.py"
    if not init_file.exists():
        with open(init_file, "w") as f:
            f.write("# 工具函数模块\n")

# 确保utils目录存在
ensure_utils_dir()

# 应用启动事件
@app.on_event("startup")
async def startup_event():
    # 初始化数据库
    logger.info("初始化数据库...")
    init_db()
    
    # 初始化模型
    logger.info("初始化模型...")
    model_initialized = await initialize_model()
    if model_initialized:
        logger.info("模型初始化成功")
    else:
        logger.warning("模型初始化失败，请检查配置")
    
    # 启动文件监视器
    logger.info("启动文件监视器...")
    start_file_watcher()
    
    logger.info("应用启动完成")

# 应用关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("应用关闭")

# 如果直接运行此文件，则启动应用
if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=True
    )