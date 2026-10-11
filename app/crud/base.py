from sqlalchemy.orm import DeclarativeBase
from typing import TypeVar, Type,Generic

#bound,声明DeclarativeBase为该自定义类的上界约束，必须为其或其子类
ModelType = TypeVar("ModelType", bound=DeclarativeBase)

class CRUDBase(Generic[ModelType]): #给类开泛型

    """CRUD 基类"""
    def __init__(self, model: Type[ModelType]):
        self.model = model