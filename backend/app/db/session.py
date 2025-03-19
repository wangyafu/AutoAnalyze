from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# 创建数据库目录（如果不存在）
db_dir = Path(os.path.dirname(os.path.abspath(__file__)))
db_dir.parent.parent.joinpath('data').mkdir(exist_ok=True)

# 数据库URL
SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_dir.parent.parent}/data/AutoAnalyze.db"

# 创建SQLAlchemy引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建声明性基类
Base = declarative_base()

# 获取数据库会话的依赖函数
def get_db():
    """获取数据库会话
    
    用于FastAPI的依赖注入，提供数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()