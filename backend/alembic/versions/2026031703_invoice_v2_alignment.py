"""align invoice schema to MVP v2

Revision ID: 2026031703
Revises: 2026031702
Create Date: 2026-03-17 23:07:00
"""

from alembic import op
import sqlalchemy as sa


revision = '2026031703'
down_revision = '2026031702'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # invoice status: remove paid from MVP
    op.execute("ALTER TYPE invoicestatus RENAME TO invoicestatus_old")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('draft','finalized','sent','cancelled')")
    op.execute(
        """
        ALTER TABLE invoices
        ALTER COLUMN status TYPE invoicestatus
        USING (
          CASE status::text
            WHEN 'paid' THEN 'sent'
            ELSE status::text
          END
        )::invoicestatus
        """
    )
    op.execute("DROP TYPE invoicestatus_old")

    # invoices extensions
    op.add_column('invoices', sa.Column('delivery_date', sa.Date(), nullable=True))
    op.execute("UPDATE invoices SET delivery_date = invoice_date WHERE delivery_date IS NULL")
    op.alter_column('invoices', 'delivery_date', nullable=False)

    # invoice_items extensions
    invoice_line_status = sa.Enum('uninvoiced', 'partially_invoiced', 'invoiced', 'cancelled', name='invoice_line_status')
    invoice_line_status.create(op.get_bind(), checkfirst=True)

    op.add_column('invoice_items', sa.Column('billable_qty', sa.Numeric(12, 3), nullable=True))
    op.add_column('invoice_items', sa.Column('billable_uom', sa.String(length=32), nullable=True))
    op.add_column('invoice_items', sa.Column('invoice_line_status', invoice_line_status, nullable=False, server_default='uninvoiced'))

    op.alter_column('invoice_items', 'unit_price', new_column_name='sales_unit_price')
    op.alter_column('invoice_items', 'amount', new_column_name='line_amount')

    op.add_column('invoice_items', sa.Column('unit_cost_basis', sa.Numeric(12, 2), nullable=True))
    op.add_column('invoice_items', sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
    op.add_column('invoice_items', sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))

    op.create_check_constraint('ck_invoice_items_sales_unit_price_nonneg', 'invoice_items', 'sales_unit_price >= 0')
    op.create_index('ix_invoices_status', 'invoices', ['status'])
    op.create_index('ix_invoice_items_order_item_id', 'invoice_items', ['order_item_id'])


def downgrade() -> None:
    op.drop_index('ix_invoice_items_order_item_id', table_name='invoice_items')
    op.drop_index('ix_invoices_status', table_name='invoices')
    op.drop_constraint('ck_invoice_items_sales_unit_price_nonneg', 'invoice_items', type_='check')

    op.drop_column('invoice_items', 'updated_at')
    op.drop_column('invoice_items', 'created_at')
    op.drop_column('invoice_items', 'unit_cost_basis')

    op.alter_column('invoice_items', 'line_amount', new_column_name='amount')
    op.alter_column('invoice_items', 'sales_unit_price', new_column_name='unit_price')

    op.drop_column('invoice_items', 'invoice_line_status')
    op.drop_column('invoice_items', 'billable_uom')
    op.drop_column('invoice_items', 'billable_qty')

    sa.Enum(name='invoice_line_status').drop(op.get_bind(), checkfirst=True)

    op.drop_column('invoices', 'delivery_date')

    op.execute("ALTER TYPE invoicestatus RENAME TO invoicestatus_new")
    op.execute("CREATE TYPE invoicestatus AS ENUM ('draft','finalized','sent','paid','cancelled')")
    op.execute(
        """
        ALTER TABLE invoices
        ALTER COLUMN status TYPE invoicestatus
        USING (
          CASE status::text
            WHEN 'sent' THEN 'sent'
            ELSE status::text
          END
        )::invoicestatus
        """
    )
    op.execute("DROP TYPE invoicestatus_new")
