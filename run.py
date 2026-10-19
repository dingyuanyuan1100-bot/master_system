from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from app.api.v1 import goods, user, auth,seckill
from app.db.redis import redis_client
from contextlib import asynccontextmanager

#新增测试方法 启动的时候开始 关闭的时候就停止
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用的生命周期管理"""
    try:
        await redis_client.ping()
        print("Redis连接成功")
    except Exception as e:
        print("连接失败",e)

    yield #上方是启动阶段，下方是关闭阶段

    await redis_client.close()
    print("redis连接已关闭")

app = FastAPI(title="商城系统",lifespan = lifespan)
# 挂载路由 —— 统一加 /api/v1 前缀
app.include_router(goods.router, prefix="/api/v1")
app.include_router(user.router, prefix="/api/v1")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(seckill.router, prefix="/api/v1")
#跨域资源共享
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # 前端开发地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
