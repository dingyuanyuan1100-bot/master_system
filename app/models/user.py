from sqlalchemy.orm import Mapped,mapped_column
from app.db.base import Base,BaseModel
from sqlalchemy import String


class User(BaseModel):
    __tablename__ = 'user'

    name     : Mapped[str]      = mapped_column(String(50),nullable=False,comment="用户名")
    password : Mapped[str]      = mapped_column(String(255),nullable=False,comment="用户密码")
    email    : Mapped[str|None] = mapped_column(String(100),comment="用户邮箱")