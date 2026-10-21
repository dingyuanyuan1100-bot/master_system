import asyncio
import json
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from app.db.redis import redis_client
from app.db.db_init import async_session
from app.models.goods import Goods
from app.models.order import Orders

ORDER_QUEUE = "seckill:orders"          #正常待处理队列
FAILED_QUEUE = "seckill:orders:failed"  #落库失败的死信队列


async def rollback_redis(message: dict):
    """落库失败时把 redis 的库存和防重标记还回去，避免库存凭空消失、用户再也抢不了"""
    goods_id = message["product_id"]
    await redis_client.incr(f"seckill:stock:{goods_id}")
    await redis_client.srem(f"seckill:bought:{goods_id}", str(message["user_id"]))


async def process_order(message: dict):
    """处理单个订单消息，写入数据库"""
    async with async_session() as session:  #每处理一条消息开一个会话
        try:
            #扣数据库库存：redis 只是前置闸门，数据库库存才是最终账本
            #这里和建订单放在同一个事务里，成功一起成功，失败一起回滚
            deducted = await session.execute(
                update(Goods)
                .where(Goods.id == message["product_id"], Goods.seckill_stock > 0)
                .values(seckill_stock=Goods.seckill_stock - 1)
            )
            if deducted.rowcount == 0:
                raise RuntimeError(f"数据库库存不足 goods_id={message['product_id']}")

            #把队列里的消息还原成一条订单记录
            order = Orders(
                order_no=message["order_no"],
                user_id=message["user_id"],
                product_id=message["product_id"],
                product_price=message["product_price"],
                status=message["status"],
            )
            session.add(order)
            await session.commit()  #提交事务，写入数据库
            print(
                f"订单创建成功 | 订单号:{message['order_no']} | "
                f"用户ID:{message['user_id']} | 商品ID:{message['product_id']}"
            )

        except IntegrityError:
            #order_no 有唯一索引：说明这条消息之前已经处理过了（消息重复投递）
            #这种情况不能再回滚库存，否则同一单会被退两次
            await session.rollback()
            exists = await session.execute(
                select(Orders.id).where(Orders.order_no == message["order_no"])
            )
            if exists.scalar() is not None:
                print(f"订单号重复，跳过 | 订单号:{message['order_no']}")
            else:
                print(f"订单写入失败（约束冲突）| 订单号:{message['order_no']}")
                await rollback_redis(message)
                await redis_client.lpush(FAILED_QUEUE, json.dumps(message, ensure_ascii=False))

        except Exception as e:
            await session.rollback()  #事务回滚
            print(f"订单创建失败 | 订单号:{message['order_no']} | {e}")
            await rollback_redis(message)  #把 redis 预扣的库存还回去
            await redis_client.lpush(FAILED_QUEUE, json.dumps(message, ensure_ascii=False))


async def consume_orders():
    print("订单消费者已经启动，等待秒杀消息")
    while True:
        try:
            #阻塞式弹出（队列空的时候就等），超时5秒避免卡死
            result = await redis_client.blpop(ORDER_QUEUE, timeout=5)
            if result is None:
                continue
            #返回的是一个元组 (key, value)
            _, message_str = result
            message = json.loads(message_str)  #字符串反序列化成字典，只能反序列化一次
            await process_order(message)

        except asyncio.CancelledError:
            print("订单消费者已停止")
            raise
        except Exception as e:
            print(f"消费者异常 | {e}")
            await asyncio.sleep(1)  #出错等待1s重新从 while True 开始


async def main():
    await redis_client.ping()
    print("redis连接成功")
    await consume_orders()


if __name__ == "__main__":
    asyncio.run(main())
