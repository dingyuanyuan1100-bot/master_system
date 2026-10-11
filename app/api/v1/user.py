from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps import get_current_user
from app.models import User
from app.schemas.user import UserCreate, UserResponse
from app.db.db_init import get_db
from app.crud.user import user_crud

router = APIRouter(prefix="/user", tags=["用户管理"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in:UserCreate, db: AsyncSession = Depends(get_db)):
    username = await user_crud.is_exist(db, user_in.name,user_in.phone)
    if  username :
        raise HTTPException(status_code=400,detail="用户名已存在或手机号已注册")
    return await user_crud.create(db, obj_in=user_in.model_dump())

@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK,summary="获取用户当前数据")
async def get_me( current_user:User = Depends(get_current_user) ):
    return current_user



