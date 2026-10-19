from fastapi import FastAPI
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from app.api.v1 import goods, user, auth,seckill

app = FastAPI(title="商城系统")
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
