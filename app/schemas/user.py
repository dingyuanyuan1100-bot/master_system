from datetime import datetime

from pydantic import Field      #字段校验规则的"说明书"

from pydantic import BaseModel  #Pydantic 基类，继承它才获得校验或解析能力


class UserBase(BaseModel):
    name    : str = Field(...,min_length=1 , max_length=50, description="用户name")
    phone   : str = Field(...,min_length=11, max_length=11, description="用户手机号")

class UserCreate(UserBase):
    password: str = Field(..., min_length=1 , max_length=50, description="用户密码")

class UserResponse(UserBase):
    id      : int
    register_time: datetime

    class Config:
        from_attributes = True