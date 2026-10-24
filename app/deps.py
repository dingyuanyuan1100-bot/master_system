from fastapi import Depends,HTTPException,Response,status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.db.db_init import get_db
from app.crud.user import user_crud

#自定义OAuth2PasswordBrarer,没有token的时候信息变中文
class OAuth2PasswordBrarer(OAuth2PasswordBearer):
    #__init__ 创建时候执行。 __call__ 调用时执行
    async def __call__(self, response: Response) ->str:
        try:
            return await super().__call__(response)
        except HTTPException:
            raise HTTPException(
                status_code=401,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )

#告诉fastapi：token 从哪个地址获取
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme),db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    #验证token
    payload = await verify_token(token)
    if payload is None:
        raise credentials_exception

    #从token中取出用户id（登录时 sub 里存的是 str(用户id)，不是用户名）
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    #查数据库，确认用户是否存在
    user = await user_crud.get_by_id(db, id=int(user_id))
    if user is None:
        raise credentials_exception
    #通过返回所有对象
    return user