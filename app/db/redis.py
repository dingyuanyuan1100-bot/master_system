import redis.asyncio as aioredis
from app.core.confing import settings

#创建redis异步连接池（从URL，直接生成，平常就拿这个client发命令）
redis_client : aioredis.Redis = aioredis.from_url(
    settings.REDIS_URL,
    encoding="utf-8",
    decode_responses=True,#自动把字节转成字符串
)

async def get_redis_client() -> aioredis.Redis:
    """依赖注入用的redis客户端（接口里想用redis的时候，depends(get_redis_client)）"""
    return redis_client