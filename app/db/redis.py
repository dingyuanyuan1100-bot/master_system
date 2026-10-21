import redis.asyncio as aioredis
from app.core.confing import settings
from datetime import datetime
from app.models.goods import Goods
from sqlalchemy import select

#创建redis异步连接池（从URL，直接生成，平常就拿这个client发命令）
redis_client : aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,#自动把字节转成字符串
)

async def get_redis_client() -> aioredis.Redis:
    """依赖注入用的redis客户端（接口里想用redis的时候，depends(get_redis_client)）"""
    return redis_client

async def preheat_seckill_stock( db_session ):
    """
    库存预热
    :param db_session:
    :return:
    """
    now = datetime.now()

    #查询所有秒杀商品
    result = await db_session.execute(
        select(Goods)
        .where(Goods.seckill_price >0)
    )

    goods_list = result.scalars().all()

    count = 0
    for good in goods_list:
        key = f"seckill:stock:{good.id}"                #seckill:stock:1 = 10
        await redis_client.set(key, good.seckill_stock) #把库存数字写进redis
        count +=1
    print(f"{count}种商品已写入redis")
    return count
