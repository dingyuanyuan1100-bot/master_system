#创建异步引擎
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from app.core.confing import settings

engine = create_async_engine(
    settings.DATABASE_URL,  #导入提前写好的数据库配置地址
    pool_size=10,           #常驻连接池
    max_overflow=5,         #常驻满了后可以额外多开的连接池数量
    pool_timeout=30,        #超时断开，防止僵尸进程
    echo=False,              #打印sql语句用的

)
#创建会话
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,    #声明生成的的是异步会话类
    expire_on_commit=False, #关闭前使用查询出来的ORM对象全部过期，需要重新查询数据库
    autoflush=False,
)
#依赖注入数据库会话生成器
async def get_db():
    async with async_session()  as session :
        try:
            yield session
        finally:
            await session.close()