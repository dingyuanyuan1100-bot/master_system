import random
import string
from datetime import timedelta,datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.goods import goods_crud
from app.crud.order import orders_crud
from app.db.db_init import get_db
from app.deps import get_current_user
from app.models.order import Orders
from app.models.user import User
from app.crud.seckillResult import good_seckill
from app.schemas.order import SeckillResult, OrderResponse

router = APIRouter(prefix="/seckill", tags=["秒杀商品"])

#生成随机订单号
def generate_order_no()->str:
    chars = string.ascii_uppercase + string.digits
    return 'SK'+"".join(random.choices(chars,k=8))

#秒杀请求接口
@router.post("/goods/{goods_id}",response_model=SeckillResult,summary="秒杀商品")
async def seckill(
        goods_id:int,#路径中{goods_id}
        current_user:User = Depends(get_current_user),#靠依赖注入当前登录用户，没登录到不了这里
        db: AsyncSession = Depends(get_db)#数据库的会话也注入进来，

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
        else:
            deducted = await good_seckill.decreate_seckill_stock(db, good_id=goods_id)
            if not deducted:
                raise HTTPException(status_code=409,detail="手慢了")
            else:
                #创建订单
                order =  Orders(
                    order_no = generate_order_no(),
                    user_id = current_user.id ,
                    product_id = goods_id ,
                    product_price = good.seckill_price,
                    status = 0, #订单待支付状态
                )
                db.add( order ) #把订单加进对话
                await db.commit() #提交事务
                await db.refresh(order) #重新拉一下拿到数据库生成的id

                return SeckillResult(
                    goods_id=goods_id,
                    order_id=order.id,
                    order_no= order.order_no,
                    order_status=order.status,
                    create_datetime=order.register_time,
                    update_datetime=order.update_time,
                    order_name=good.name,
                    order_price=order.product_price,
                    message="秒杀成功，请尽快支付",
                )

@router.post("/my_orders",response_model=list[OrderResponse],summary="我的订单")
async def my_orders(
        db: AsyncSession = Depends(get_db),
        current_user:User = Depends(get_current_user)

):
    #查询当前登录用户订单列表
    orders = await orders_crud.get_orders_list(db, current_user.id)
    result = []
    for order in orders:
        #注意：get_by_id 是异步方法必须 await；订单表存的是 product_id 不是 goods_id
        good = await goods_crud.get_by_id(db, id=order.product_id)

        result.append(
            OrderResponse(
                id=order.id,
                user_id=order.user_id,
                order_id=order.id,
                order_no=order.order_no,
                order_name=good.name if good else "该商品已下架",
                good_price=good.price if good else 0.0,   #商品现价
                order_price=order.product_price,          #下单快照价（秒杀价）
                status=order.status,
                create_time=order.register_time,
                update_time=order.update_time,
            )
        )
    return result

@router.post("/cancel_orders",summary="取消订单")
async def cancel_orders(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user:User = Depends(get_current_user),
):
    #查订单
    orders = await orders_crud.get_order_by_id(db, current_user=current_user,order_id=order_id)
    if not orders:
        raise HTTPException(status_code=400,detail="订单不存在")
    if orders.status != 0:
        raise HTTPException(status_code=400,detail="当前订单状态不能取消")
    orders.status = -1 #-1已取消,0待支付,1 已支付，待发货

    #归还库存
    await good_seckill.create_seckill_stock(db, good_id=orders.product_id)
    await db.commit()
    await db.refresh(orders)
    return orders
