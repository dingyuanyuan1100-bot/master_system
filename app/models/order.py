from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.orm import mapped_column,Mapped
from app.db.base import Base, BaseModel


class Orders(BaseModel):
    __tablename__ = 'orders'
    #用外键指向下单的人id
    user_id : Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=False,
        comment="订单对应用户id"
    )
    product_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('goods.id'),
        nullable=False,
        comment="订单对应商品id"
    )
    product_price: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="订单对应金额"
    )
    status: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="订单状态码"
    )



