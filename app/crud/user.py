from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.crud.base import CRUDBase
from app.models.user import User


class UserCRUD(CRUDBase[User]):
    """用户数据操作"""

    #异步函数所有的self都是继承自CRUD的model
    async def create(self, db: AsyncSession, *, obj_in: dict) -> User:
        """创建用户：强制密码哈希"""
        user_obj = self.model(**obj_in) #此处的model是继承于CRUD基类里面的
        user_obj.password = await get_password_hash(user_obj.password)   # 用对象属性，不用 obj_in['password']
        db.add(user_obj)
        await db.commit()
        await db.refresh(user_obj)
        return user_obj

    async def get_by_name(self, db: AsyncSession, name: str) -> User | None:
        result = await db.execute(select(User).where(User.name == name))
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == id))
        return result.scalar_one_or_none()

    async def is_exist(self, db: AsyncSession, name: str, phone: str) -> bool:
        result = await db.execute(
            select(User.id).where(or_(User.name == name, User.phone == phone))
        )
        return result.scalar() is not None


user_crud = UserCRUD(User)
