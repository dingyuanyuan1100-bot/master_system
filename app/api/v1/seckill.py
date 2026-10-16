from datetime import timedelta,datetime
from itertools import product

from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.crud.user import user_crud
from app.crud.goods import goods_crud
from app.db.db_init import get_db
from app.core.security import verify_password, create_token
from app.core.confing import settings
from app.deps import get_current_user
from app.models.order import Orders
from app.models.user import User
from app.crud.user import user_crud
from app.crud.seckillResult import good_seckill
router = APIRouter(prefix="/seckill", tags=["秒杀商品"])

@router.post("/{goods_id}")
async def seckill(
        goods_id:int,#路径中{goods_id}
        current_user:User = Depends(get_current_user),#靠依赖注入当前登录用户，没登录到不了这里
        db: AsyncSession = Depends(get_db)#数据库的会话也注入进来
):
    """
    秒杀下单接口
    1.检查商品是否存在
    2.检查秒杀是否在进行中
    3.扣减秒杀库存
    4、创建订单
    """
    good = await goods_crud.get_by_id(db, id=goods_id)
    if not good:
        raise HTTPException(status_code=404,detail="商品不存在")
    if good:
        datetime_now = datetime.now()
        if not good.seckill_price:
            raise HTTPException(status_code=409,detail="该商品不是秒杀商品")
        elif not good.seckill_stock:
            raise HTTPException(status_code=409,detail="商品库存不足")
        elif not (good.seckill_datetime_start < datetime_now < good.seckill_datetime_end):
            raise HTTPException(status_code=409,detail="不在秒杀活动时间内")
        elif good.seckill_stock<=0:
            raise HTTPException(status_code=409,detail="商品库存不足")
        else:
            deducted = await good_seckill.decreate_seckill_stock(db, goods_id=goods_id)
            if not deducted:
                raise HTTPException(status_code=409,detail="手慢了")
            else:
                #创建订单
                order =  Orders(
                    user_id = current_user.id ,
                    product_id = goods_id ,
                    product_price = good.seckill_price,
                    status = 0, #订单待支付状态
                )
                db.add( order ) #把订单加进对话
                await db.commit() #提交事务
                await db.refresh(order) #重新拉一下拿到数据库生成的id

                return {
                    "code" : 200 ,
                    "msg" : "订单已生成，请前往支付" ,
                    "data" : {
                        "goods_id" : goods_id,
                        "order_id":order.id,
                        "order_status" : order.status,
                        "create_datetime": order.register_time,
                        "update_datetime": order.update_time,
                    }
                }


