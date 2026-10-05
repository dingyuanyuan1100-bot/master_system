from app.crud.base import CRUDBase
from app.models.goods import Goods

#创建goods_curd的时候自动加上Goods做基类
goods_crud = CRUDBase(Goods)