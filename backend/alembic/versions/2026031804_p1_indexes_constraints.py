"""p1 indexes and data integrity constraints

Revision ID: 2026031804
Revises: 2026031803
Create Date: 2026-03-18 17:03:00
"""

from alembic import op


revision = '2026031804'
down_revision = '2026031803'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('ix_order_items_order_id_line_status', 'order_items', ['order_id', 'line_status'])
    op.create_index('ix_supplier_allocations_order_item_split', 'supplier_allocations', ['order_item_id', 'is_split_child'])
    op.create_index('ix_invoices_customer_status_date', 'invoices', ['customer_id', 'status', 'invoice_date'])
    op.create_index('ix_purchase_results_allocation_status', 'purchase_results', ['allocation_id', 'result_status'])

    op.create_check_constraint(
        'ck_supplier_allocations_final_qty_positive',
        'supplier_allocations',
        '(final_qty IS NULL) OR (final_qty > 0)',
    )
    op.create_check_constraint(
        'ck_purchase_results_shortage_qty_nonneg',
        'purchase_results',
        '(shortage_qty IS NULL) OR (shortage_qty >= 0)',
    )


def downgrade() -> None:
    op.drop_constraint('ck_purchase_results_shortage_qty_nonneg', 'purchase_results', type_='check')
    op.drop_constraint('ck_supplier_allocations_final_qty_positive', 'supplier_allocations', type_='check')

    op.drop_index('ix_purchase_results_allocation_status', table_name='purchase_results')
    op.drop_index('ix_invoices_customer_status_date', table_name='invoices')
    op.drop_index('ix_supplier_allocations_order_item_split', table_name='supplier_allocations')
    op.drop_index('ix_order_items_order_id_line_status', table_name='order_items')
