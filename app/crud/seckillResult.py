from app.crud.base import CRUDBase
from app.models.goods import Goods
from sqlalchemy import select,update
from sqlalchemy.ext.asyncio import AsyncSession

class CRUDSeckillResult(CRUDBase[Goods]):
    """ 商品CRUD扩展秒杀_行锁并发 """
    async def decreate_seckill_stock(self,db: AsyncSession,good_id: int):

        #本质是将查询与扣库存合成一步操作
        stmt = (update(Goods)
                .where(Goods.id == good_id,Goods.seckill_stock > 0)
                        #左边的stock代表数据库行列名，右边代表对应数据库数据的变量
                .values(seckill_stock = Goods.seckill_stock-1) #用数据库自己算，不经过python内存
                )
        result = await db.execute(stmt)
        return result.rowcount > 0 #rowcount是执行后返回的自带属性，用来记录本次更新了多少行数据

    async def create_seckill_stock(self,db: AsyncSession,good_id: int):
        stm = (update(Goods)
               .where(Goods.id == good_id)
               .values(seckill_stock = Goods.seckill_stock+1)
               )
        result = await db.execute(stm)
        return result.rowcount > 0

good_seckill = CRUDSeckillResult(Goods)