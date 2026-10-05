from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import TypeVar, Type
from sqlalchemy.sql import select
ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class CRUDBase():

    """CRUD 基类"""
    def __init__(self, model: Type[ModelType]):
        self.model = model

    #异步获取
    #根据id查询单个对象
    async def get_by_id(self,
                        session: AsyncSession,
                        id: int) -> ModelType:
        result = await session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()#获取一条记录，没有就返回None，不报错

    #分页获取多个订单
    async def get_multi(self,
                        db: AsyncSession,
                        *,
                        skip: int = 0,
                        limit: int = 100
                        )->list[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    #创建对象 = 插入
    async def create(self, db: AsyncSession, *, obj_in: dict) -> ModelType:
        """创建对象"""
        db_obj = self.model(**obj_in)   #解包
        db.add(db_obj)
        await db.commit()               #提交,真正写入数据库
        await db.refresh(db_obj)        #重新读取
        return db_obj                   #返回结果

    #修改
    async def update(self,
                     db: AsyncSession,
                     *,
                     db_obj: ModelType,
                     obj_in: dict) -> ModelType:
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    #删除
    async def delete(self,
                     db: AsyncSession,
                     *,
                     db_obj: ModelType
                     ) -> ModelType:
        obj = await self.get_by_id(db,id=db_obj.id)
        if obj:
            await db.delete(db_obj)
            await db.commit()
        return obj

