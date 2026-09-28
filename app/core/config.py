from functools import lru_cache

from pydantic_settings import BaseSettings

#BaseSettings 是pydantic提供的配置的管理基类
class Settings(BaseSettings):
    #数据库配置
    DATABASE_URL: str = 'mysql+aiomysql://root:123456root@localhost:3306/market_system?charset=utf8'

    #其他配置
    DEBUG: bool = True #debug调试
    class Config:
        env_file = '.env'

#带缓存 不用每次都去读取数据库
@lru_cache()
def get_settings():
    return Settings()


