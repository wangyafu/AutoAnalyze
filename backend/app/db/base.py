from app.db.session import Base

# 导入所有模型，确保它们在Base.metadata中注册
# 当需要创建所有表时，只需导入此模块

# 这里导入所有模型
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.execution import Execution

# 如果将来添加新模型，请在此处导入
# from models.new_model import NewModel
from app.db.session import engine
# 初始化数据库函数
def init_db():
    """
    初始化数据库，创建所有表
    
    在应用启动时调用此函数可以确保所有表都已创建
    """
    
    Base.metadata.create_all(bind=engine)