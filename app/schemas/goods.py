from datetime import datetime
from pydantic import BaseModel, Field


class GoodsBase(BaseModel):
    """商品公共字段：创建和响应都有"""
    name    : str   = Field(..., min_length=1, max_length=100, description="商品名称")
    describe: str   = Field(..., min_length=1, max_length=100, description="商品分类")
    price   : float = Field(..., gt=0, description="商品价格")
    stock   : int   = Field(..., ge=0, description="商品数量")


class GoodsCreate(GoodsBase):
    """创建商品：前端只需传基础字段，id和时间由数据库自动生成"""
    pass


class GoodsResponse(GoodsBase):
    """接口返回：多出数据库自动生成的字段"""
    id           : int
    register_time: datetime
    update_time  : datetime

    model_config = {"from_attributes": True}  # 允许直接接收ORM对象转JSON
