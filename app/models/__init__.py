from app.db.base import Base
from app.models.user import User
from app.models.goods import Goods

#模型包的入口文件
__all__ = ["User","Goods","Base"]