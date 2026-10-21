import random
import string
import json
from datetime import timedelta,datetime
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.goods import goods_crud
from app.crud.order import orders_crud
from app.db.db_init import get_db
from app.deps import get_current_user
from app.models.user import User
from app.crud.seckillResult import good_seckill
from app.schemas.order import SeckillResult, OrderResponse
from app.db.redis import redis_client

router = APIRouter(prefix="/seckill", tags=["秒杀商品"])

#生成随机订单号
def generate_order_no()->str:
    chars = string.ascii_uppercase + string.digits
    return 'SK'+"".join(random.choices(chars,k=8))

#秒杀请求接口(redis前置校验+消息队列异步下单)
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

    改进：
    1.redis set 防重复秒杀（代替查询数据库订单库）
    2.redis 原子性扣库存（代替update sql）
    3.消息队列异步创建订单
    """
    good = await goods_crud.get_by_id(db, id=goods_id)
    if not good:
        raise HTTPException(status_code=404,detail="商品不存在")

    datetime_now = datetime.now()
    if not good.seckill_price:
        raise HTTPException(status_code=409,detail="该商品不是秒杀商品")
    elif not good.seckill_stock:
        raise HTTPException(status_code=409,detail="商品库存不足")
    elif not (good.seckill_datetime_start < datetime_now < good.seckill_datetime_end):
        raise HTTPException(status_code=409,detail="不在秒杀活动时间内")
    else:
        """=============redis拦截层==================="""
        bought_key = f"seckill:bought:{goods_id}"
        stock_key = f"seckill:stock:{goods_id}"

        #通过sadd判断是否已经抢过，如果没有抢过会创建并返回1，没有抢过就会返回0
        first_time_redis = await redis_client.sadd(bought_key, str(current_user.id))
        first_time_mysql = await orders_crud.get_active_order_by_id(db,current_user=current_user,good_id=goods_id)
        if not first_time_redis or first_time_mysql :
            raise HTTPException(status_code=400,detail="你已抢过该商品")

        #这一部防止缓存被清掉后，有库存却报错的可能（nx代表只有key不存在才创建，不加的话无论key存不存在都会修改）
        if not await redis_client.exists(stock_key):
            await redis_client.set(stock_key, good.seckill_stock or 0, nx=True)

        #原子扣库存
        stock = await redis_client.decr(stock_key)
        if stock<0:
            #库存不足
            await redis_client.incr(stock_key)
            #没抢到要把防重标记摘掉，否则这个用户以后再也抢不了这个商品
            await redis_client.srem(bought_key, str(current_user.id))
            raise HTTPException(status_code=409,detail="手慢了，商品已售空")

        #投递消息到redis队列
        order_no = generate_order_no()
        msg = {
            "order_no": order_no,
            "user_id": current_user.id,
            "product_id": goods_id,
            "product_price":float(good.seckill_price),
            "status": 0,    #订单待支付状态
        }
        await redis_client.lpush("seckill:orders", json.dumps(msg))

        """
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
        """
        return SeckillResult(
            goods_id=goods_id,
            order_id=0,
            order_no= order_no,
            order_status=0,
            create_datetime=datetime_now,
            update_datetime=datetime_now,
            order_name=good.name,
            order_price=float(good.seckill_price),
            message="秒杀成功，请尽快支付，订单后台生成中",
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

    #同步回滚redis库存+移除已抢购标记
    goods_id = orders.product_id
    bought_key = f"seckill:bought:{goods_id}"
    stock_key = f"seckill:stock:{goods_id}"
    await redis_client.srem(bought_key, str(current_user.id))
    await redis_client.incr(stock_key)

    return orders
