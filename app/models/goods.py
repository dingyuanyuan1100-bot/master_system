import datetime
from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base, BaseModel
from sqlalchemy import String, Integer,text,DateTime


class Goods(BaseModel):
    #商品表
    __tablename__ = 'goods'

    name    : Mapped[str]       = mapped_column(String(100),nullable=False,comment = "商品名称")
    describe: Mapped[str]       = mapped_column(String(100),nullable=False,comment = "商品分类")
    price   : Mapped[float] = mapped_column(nullable=False,comment = "商品价格")
    stock   : Mapped[int]       = mapped_column(nullable=False,comment = "商品数量")

    #__________________秒杀的相关字段
    #秒杀价格可以为空，空代表该价格不参加秒杀，普通商品和秒杀商品共用同一个表单，靠价格区分是否秒杀
    seckill_price : Mapped[float|None] = mapped_column(nullable=True,comment="秒杀价格")
    seckill_stock : Mapped[int|None] = mapped_column(Integer,server_default=text("0"),nullable=False,comment="秒杀库存")
    seckill_datetime_start:Mapped[datetime.datetime |None] = mapped_column(DateTime,nullable=True,comment="秒杀开始时间")
    seckill_datetime_end : Mapped[datetime.datetime | None] = mapped_column(DateTime,nullable=True,comment="秒杀结束时间")