from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    "应用配置"
    #配置数据库
    DATABASE_URL: str = 'mysql+aiomysql://root:123456@127.0.0.1:3306/test1?charset=utf8mb4'

    #其他配置
    DEBUG: bool = True

    #Redis配置
    REDIS_URL: str = 'redis://127.0.0.1:6379'

    #JWT配置
    SECRET_KEY                  : str = "your-secret-key-here-change-it-in-production"    #签名密钥
    ALGORITHM                   : str = "HS256"                                           #签名算法
    ACCESS_TOKEN_EXPIRE_MINUTES : int = 60 * 24                                           #token有效期24小时

    class Config:
        env_file = '.env'

#创建缓存,确保不用每次都读取加载一次
@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()