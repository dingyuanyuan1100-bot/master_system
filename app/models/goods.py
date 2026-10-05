from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base, BaseModel
from sqlalchemy import String

class Goods(BaseModel):
    #商品表
    __tablename__ = 'goods'

    name    : Mapped[str]       = mapped_column(String(100),nullable=False,comment = "商品名称")
    describe: Mapped[str]       = mapped_column(String(100),nullable=False,comment = "商品分类")
    price   : Mapped[float] = mapped_column(nullable=False,comment = "商品价格")
    stock   : Mapped[int]       = mapped_column(nullable=False,comment = "商品数量")