from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import get_settings

#创建异步引擎
engine = create_async_engine(
    get_settings().DATABASE_URL,
    echo=get_settings.DEBUG,#控制台打印所有sql语句 调试的时候有用
    pool_size =10,          #连接池常驻连接数量
    max_overflow=10,        #常驻连接池满了后可以新增的最大临时连接数量（单次最高20个连接）
    pool_timeout=10,        #当所有连接池满了后新请求最多停10秒
    pool_reset_session=True #重置会话状态,避免上一个请求污染会话

)

#创建会话引擎
AsyncSessionlocal = async_sessionmaker(
    engine,                 #从里面拿取数据库连接（心脏）
    class_=AsyncSession,    #声明自己要生成的是异步会话对象AsyncSession
    expire_on_commit=False, #在异步模式下所有查询后的ORM模型对象会全部标注过期，查询过期的会直接报错
    autoflush=False,        #执行任何查询语句之前，SQLAlchemy 会先执行刷新，把内存的改动发送到数据库里面
)

#依赖注入数据库会话生成器
async def get_db():
    async with AsyncSessionlocal as session:
        yield session()