from fastapi import FastAPI
import uvicorn
from app.api.v1 import goods

#注册app应用
app = FastAPI(title="商城系统")
#挂载路由
app.include_router(goods.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)