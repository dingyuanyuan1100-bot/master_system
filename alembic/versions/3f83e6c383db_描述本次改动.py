"""描述本次改动

Revision ID: 3f83e6c383db
Revises: 8a7a4fc5fcb3
Create Date: 2026-10-17 15:16:02.830630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3f83e6c383db'
down_revision: Union[str, Sequence[str], None] = '8a7a4fc5fcb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # order_no 列已存在（手动添加，含注释），这里只补唯一约束
    op.create_unique_constraint('uq_orders_order_no', 'orders', ['order_no'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('uq_orders_order_no', 'orders', type_='unique')
    op.drop_column('orders', 'order_no')
