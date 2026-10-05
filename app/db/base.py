from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column
from sqlalchemy import func


#所有模型的基类
class Base(DeclarativeBase):
    pass

#带通用字段的抽象基类
class BaseModel(Base):
    __abstract__ = True #抽象基类
    #sqlalchemy2.0 map新写法
    id :Mapped[int] = mapped_column(primary_key=True, autoincrement=True, nullable=False,comment = "主键")
    register_time : Mapped[datetime] = mapped_column(default=func.now(),nullable=False,comment="注册时间") #不要使用datetime.datetime.now()，默认创建时间为服务器启动时间，不是注册时间
    update_time : Mapped[datetime] = mapped_column(default=func.now(),onupdate=func.now(),nullable=False,comment="更新时间")
    """
    name : Mapped[str] = mapped_column(describe="用户名",nullable=False)
    password: Mapped[str] = mapped_column(default="",nullable=False,describe="密码")
    register_time : Mapped[datetime] = mapped_column(default=func,nullable=False,describe="注册时间") #不要使用datetime.datetime.now()，默认创建时间为服务器启动时间，不是注册时间
    email : Mapped[str] = mapped_column(default="",nullable=True,describe="邮箱")
    """