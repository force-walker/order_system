"""add customers master and product version column

Revision ID: 2026031805
Revises: 2026031804
Create Date: 2026-03-18 18:08:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031805'
down_revision = '2026031804'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.UniqueConstraint('code', name='uq_customers_code'),
    )
    op.create_index('ix_customers_code', 'customers', ['code'])
    op.create_index('ix_customers_name', 'customers', ['name'])
    op.create_index('ix_customers_active', 'customers', ['active'])

    op.add_column('products', sa.Column('version', sa.Integer(), nullable=False, server_default='1'))


def downgrade() -> None:
    op.drop_column('products', 'version')

    op.drop_index('ix_customers_active', table_name='customers')
    op.drop_index('ix_customers_name', table_name='customers')
    op.drop_index('ix_customers_code', table_name='customers')
    op.drop_table('customers')
