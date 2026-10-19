from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy import text, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

class GoodsBase(BaseModel):
    """商品公共字段：创建和响应都有"""
    """秒杀商品相关字段"""
    name    : str   = Field(..., min_length=1, max_length=100, description="商品名称")
    describe: str   = Field(..., min_length=1, max_length=100, description="商品分类")
    price   : float = Field(..., gt=0, description="商品价格")
    stock   : int   = Field(..., ge=0, description="商品数量")


class GoodsCreate(GoodsBase):
    """创建商品：前端只需传基础字段，id和时间由数据库自动生成"""
    seckill_price: float | None = None
    seckill_stock: int | None = None
    seckill_datetime_start: datetime | None = None
    seckill_datetime_end: datetime | None = None


class GoodsResponse(GoodsBase):
    """接口返回：多出数据库自动生成的字段"""
    id           : int
    register_time: datetime
    update_time  : datetime

    # 秒杀字段：数据库里早就有，但之前没放进响应模型，被 Pydantic 过滤掉了，
    # 导致前端永远拿不到秒杀价 / 秒杀库存 / 活动时间。这里把已有列暴露出来即可。
    seckill_price          : float | None    = None
    seckill_stock          : int | None      = None
    seckill_datetime_start : datetime | None = None
    seckill_datetime_end   : datetime | None = None


    model_config = {"from_attributes": True}  # 允许直接接收ORM对象转JSON
