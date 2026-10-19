from fastapi import Depends
from sqlalchemy import select,values
from app import deps
from app.crud.base import CRUDBase
from app.models import User
from app.models.order import Orders
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List


class CRUDOrder(CRUDBase[Orders]):
    #查询用户个人的订单
    async def get_orders_list(self,
                              db:AsyncSession,
                              user_id:int,
                              *,
                              skip: int = 0,
                              limit: int = 100,
                              )->List[Orders] :
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == user_id)      #只查该用户id的订单
            .order_by(self.model.register_time.desc()) #按照创建时间倒序，最新时间排前面
            .offset(skip)                              #从第几条开始
            .limit(limit)                              #最多拿多少条
        )
        return result.scalars().all()                   #把结果转换成oreders对象列表

    async def get_order_by_id(self,
                              db:AsyncSession,
                              *,
                              current_user: User,
                              order_id: int,
                              ):
        result = await db.execute(
            select(self.model)
            .where(self.model.user_id == current_user.id,self.model.id == order_id)
        )
        return result.scalars().one_or_none()






orders_crud = CRUDOrder(Orders)