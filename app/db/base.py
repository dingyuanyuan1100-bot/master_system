from sqlalchemy import Column
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


class BaseModel(DeclarativeBase):
    __abstract__ = True

    id:Mapped[int] = Column(Integer, primary_key=True)