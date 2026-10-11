from datetime import timedelta, datetime, timezone
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.confing import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    #验证密码
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    加密密码（bcrypt最大支持72个字节 超长的密码会被截断）
    这里用[:72], 显式截断  避免新版本 bcrypt4.1+ 抛异常
    """
    return pwd_context.hash(password[:72])

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """

    :param data:         放进 token 的数据
    :param expires_delta: 自定义过期时长，默认 24 小时
    :return:             JWT字符串
    """

    to_encode = data.copy() #copy一个变量，用完销毁
    # 过期时间 = 现在 + (自定义时长 或 默认24小时) 如果有expires_delta就返回expires_delta，没有就默认ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})                       # 过期时间塞进 payload
    #用密钥签名生成 Token
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

#Token验证
def verify_token(token: str)->Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload   # 成功：返回解析出的 payload
    except JWTError:
        return None      # 失败：返回 None
