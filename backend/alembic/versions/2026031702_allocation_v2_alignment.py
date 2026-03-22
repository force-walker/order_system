"""align allocation and purchase results to MVP v2

Revision ID: 2026031702
Revises: 2026031701
Create Date: 2026-03-17 23:06:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031702'
down_revision = '2026031701'
branch_labels = None
depends_on = None


def upgrade() -> None:
    stockout_policy = sa.Enum('backorder', 'substitute', 'cancel', 'split', name='stockout_policy')
    stockout_policy.create(op.get_bind(), checkfirst=True)

    op.add_column('supplier_allocations', sa.Column('target_price', sa.Numeric(12, 2), nullable=True))
    op.add_column('supplier_allocations', sa.Column('stockout_policy', stockout_policy, nullable=True))

    op.add_column('purchase_results', sa.Column('supplier_id', sa.Integer(), nullable=True))
    op.add_column('purchase_results', sa.Column('final_unit_cost', sa.Numeric(12, 2), nullable=True))
    op.add_column('purchase_results', sa.Column('shortage_qty', sa.Numeric(12, 3), nullable=True))
    op.add_column('purchase_results', sa.Column('shortage_policy', stockout_policy, nullable=True))
    op.add_column('purchase_results', sa.Column('invoiceable_flag', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('purchase_results', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))

    # v2 result status as string code set
    op.add_column('purchase_results', sa.Column('result_status_v2', sa.String(length=32), nullable=False, server_default='not_filled'))
    op.execute(
        """
        UPDATE purchase_results
        SET result_status_v2 = CASE result_status::text
          WHEN 'full' THEN 'filled'
          WHEN 'partial' THEN 'partially_filled'
          WHEN 'substitute' THEN 'substituted'
          WHEN 'failed' THEN 'not_filled'
          ELSE 'not_filled'
        END
        """
    )
    op.drop_column('purchase_results', 'result_status')
    op.alter_column('purchase_results', 'result_status_v2', new_column_name='result_status')

    op.create_check_constraint('ck_purchase_results_purchased_qty_positive', 'purchase_results', 'purchased_qty > 0')
    op.create_index('ix_purchase_results_supplier_id', 'purchase_results', ['supplier_id'])


def downgrade() -> None:
    op.drop_index('ix_purchase_results_supplier_id', table_name='purchase_results')
    op.drop_constraint('ck_purchase_results_purchased_qty_positive', 'purchase_results', type_='check')

    op.add_column('purchase_results', sa.Column('result_status', sa.String(length=32), nullable=True))
    op.execute(
        """
        UPDATE purchase_results
        SET result_status = CASE result_status
          WHEN 'filled' THEN 'full'
          WHEN 'partially_filled' THEN 'partial'
          WHEN 'substituted' THEN 'substitute'
          ELSE 'failed'
        END
        """
    )
    op.drop_column('purchase_results', 'result_status')

    op.drop_column('purchase_results', 'updated_at')
    op.drop_column('purchase_results', 'invoiceable_flag')
    op.drop_column('purchase_results', 'shortage_policy')
    op.drop_column('purchase_results', 'shortage_qty')
    op.drop_column('purchase_results', 'final_unit_cost')
    op.drop_column('purchase_results', 'supplier_id')

    op.drop_column('supplier_allocations', 'stockout_policy')
    op.drop_column('supplier_allocations', 'target_price')

    sa.Enum(name='stockout_policy').drop(op.get_bind(), checkfirst=True)
