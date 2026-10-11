from datetime import timedelta
from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.crud.user import user_crud
from app.db.db_init import get_db
from app.core.security import verify_password, create_token
from app.core.confing import settings

router = APIRouter(prefix="/auth",tags=["认证管理"],)

@router.post("/login", status_code=200,summary="用户登录")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db:AsyncSession=Depends(get_db)):
    result = await user_crud.get_by_name(db, form_data.username)
    if not result :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, result.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )


    #设置JWT
    access_token_expires = timedelta( minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES )#计算token存活时间

    access_token = create_token(
        data={"sub":str(result.id)},        #往token里面塞的数据
        expires_delta=access_token_expires, #存活时长
    )
    return {
        "access_token":access_token,
        "token_type":"bearer",
    }