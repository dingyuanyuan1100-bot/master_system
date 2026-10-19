from datetime import datetime

from pydantic import BaseModel



class OrderResponse(BaseModel):
    """把整个订单返回给前端"""
    id:int
    user_id:int
    order_id:int
    order_no:str
    order_name:str
    good_price:float
    order_price:float
    status:int

    create_time:datetime
    update_time:datetime

    class Config:
        #让 pydantic 能够执行从数据库对象ORM对象来读数据不然得手动一个一个搬字段
        from_attributes = True

class SeckillResult(BaseModel):
    """秒杀成功后专门返回给前端看的关键信息"""
    goods_id: int
    order_id: int
    order_no: str
    order_status: int
    create_datetime: datetime
    update_datetime: datetime
    order_name: str
    order_price: float
    message: str