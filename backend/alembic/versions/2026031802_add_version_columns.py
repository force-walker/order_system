"""add optimistic lock version columns

Revision ID: 2026031802
Revises: 2026031801
Create Date: 2026-03-18 00:49:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031802'
down_revision = '2026031801'
branch_labels = None
depends_on = None


def upgrade() -> None:
    for table in ['orders', 'order_items', 'supplier_allocations', 'invoices', 'invoice_items']:
        op.add_column(table, sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    for table in ['invoice_items', 'invoices', 'supplier_allocations', 'order_items', 'orders']:
        op.drop_column(table, 'version')
