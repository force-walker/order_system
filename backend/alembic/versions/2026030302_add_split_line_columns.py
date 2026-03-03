"""add split-line columns to supplier_allocations

Revision ID: 2026030302
Revises: 2026030301
Create Date: 2026-03-03 02:25:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2026030302'
down_revision = '2026030301'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('supplier_allocations', sa.Column('split_group_id', sa.String(length=64), nullable=True))
    op.add_column('supplier_allocations', sa.Column('parent_allocation_id', sa.Integer(), nullable=True))
    op.add_column('supplier_allocations', sa.Column('is_split_child', sa.Boolean(), nullable=False, server_default='false'))

    op.create_foreign_key(
        'fk_supplier_allocations_parent_allocation_id',
        'supplier_allocations',
        'supplier_allocations',
        ['parent_allocation_id'],
        ['id'],
    )
    op.create_index('idx_allocations_split_group_id', 'supplier_allocations', ['split_group_id'])
    op.create_index('idx_allocations_parent_allocation_id', 'supplier_allocations', ['parent_allocation_id'])
    op.create_index('idx_allocations_is_split_child', 'supplier_allocations', ['is_split_child'])


def downgrade() -> None:
    op.drop_index('idx_allocations_is_split_child', table_name='supplier_allocations')
    op.drop_index('idx_allocations_parent_allocation_id', table_name='supplier_allocations')
    op.drop_index('idx_allocations_split_group_id', table_name='supplier_allocations')
    op.drop_constraint('fk_supplier_allocations_parent_allocation_id', 'supplier_allocations', type_='foreignkey')

    op.drop_column('supplier_allocations', 'is_split_child')
    op.drop_column('supplier_allocations', 'parent_allocation_id')
    op.drop_column('supplier_allocations', 'split_group_id')
