"""init schema

Revision ID: 2026030301
Revises:
Create Date: 2026-03-03 01:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2026030301'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pricing_basis = sa.Enum('per_order_uom', 'per_kg', name='pricingbasis', create_type=False)
    order_status = sa.Enum('new', 'confirmed', 'purchasing', 'shipped', 'delivered', 'completed', 'cancelled', name='orderstatus')
    line_status = sa.Enum('open', 'allocated', 'purchased', 'invoiced', 'cancelled', name='linestatus')
    result_status = sa.Enum('full', 'partial', 'failed', 'substitute', name='resultstatus')
    invoice_status = sa.Enum('draft', 'finalized', 'sent', 'paid', 'cancelled', name='invoicestatus')
    audit_action = sa.Enum('create', 'update', 'status_change', 'override', name='auditaction')

    pricing_basis.create(op.get_bind(), checkfirst=True)
    order_status.create(op.get_bind(), checkfirst=True)
    line_status.create(op.get_bind(), checkfirst=True)
    result_status.create(op.get_bind(), checkfirst=True)
    invoice_status.create(op.get_bind(), checkfirst=True)
    audit_action.create(op.get_bind(), checkfirst=True)

    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('order_uom', sa.String(length=32), nullable=False),
        sa.Column('purchase_uom', sa.String(length=32), nullable=False),
        sa.Column('invoice_uom', sa.String(length=32), nullable=False),
        sa.Column('is_catch_weight', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('weight_capture_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pricing_basis_default', pricing_basis, nullable=False),
        sa.Column('rounding_weight_scale', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('rounding_amount_scale', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('sku'),
    )
    op.create_index('idx_products_sku', 'products', ['sku'])
    op.create_index('idx_products_active', 'products', ['active'])

    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_no', sa.String(length=64), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('order_datetime', sa.DateTime(), nullable=False),
        sa.Column('delivery_type', sa.String(length=32), nullable=False),
        sa.Column('delivery_address_snapshot', sa.Text(), nullable=True),
        sa.Column('payment_method', sa.String(length=64), nullable=True),
        sa.Column('payment_status', sa.String(length=64), nullable=True),
        sa.Column('status', order_status, nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('order_no'),
    )
    op.create_index('idx_orders_customer_id', 'orders', ['customer_id'])
    op.create_index('idx_orders_status', 'orders', ['status'])
    op.create_index('idx_orders_order_datetime', 'orders', ['order_datetime'])

    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('orders.id'), nullable=False),
        sa.Column('product_id', sa.Integer(), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('ordered_qty', sa.Numeric(12, 3), nullable=False),
        sa.Column('ordered_uom', sa.String(length=32), nullable=False),
        sa.Column('estimated_weight_kg', sa.Numeric(12, 3), nullable=True),
        sa.Column('actual_weight_kg', sa.Numeric(12, 3), nullable=True),
        sa.Column('pricing_basis', pricing_basis, nullable=False),
        sa.Column('unit_price_order_uom', sa.Numeric(12, 2), nullable=True),
        sa.Column('unit_price_per_kg', sa.Numeric(12, 2), nullable=True),
        sa.Column('discount_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('tax_code', sa.String(length=32), nullable=False),
        sa.Column('line_subtotal', sa.Numeric(12, 2), nullable=True),
        sa.Column('line_tax', sa.Numeric(12, 2), nullable=True),
        sa.Column('line_total', sa.Numeric(12, 2), nullable=True),
        sa.Column('line_status', line_status, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_order_items_order_id', 'order_items', ['order_id'])
    op.create_index('idx_order_items_product_id', 'order_items', ['product_id'])
    op.create_index('idx_order_items_line_status', 'order_items', ['line_status'])

    op.create_table(
        'supplier_allocations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_item_id', sa.Integer(), sa.ForeignKey('order_items.id'), nullable=False),
        sa.Column('suggested_supplier_id', sa.Integer(), nullable=True),
        sa.Column('final_supplier_id', sa.Integer(), nullable=True),
        sa.Column('suggested_qty', sa.Numeric(12, 3), nullable=True),
        sa.Column('suggested_uom', sa.String(length=32), nullable=True),
        sa.Column('final_qty', sa.Numeric(12, 3), nullable=True),
        sa.Column('final_uom', sa.String(length=32), nullable=True),
        sa.Column('is_manual_override', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('override_reason_code', sa.String(length=64), nullable=True),
        sa.Column('override_note', sa.Text(), nullable=True),
        sa.Column('overridden_by', sa.String(length=64), nullable=True),
        sa.Column('overridden_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )
    op.create_index('idx_allocations_order_item_id', 'supplier_allocations', ['order_item_id'])
    op.create_index('idx_allocations_final_supplier_id', 'supplier_allocations', ['final_supplier_id'])
    op.create_index('idx_allocations_manual_override', 'supplier_allocations', ['is_manual_override'])

    op.create_table(
        'purchase_results',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('allocation_id', sa.Integer(), sa.ForeignKey('supplier_allocations.id'), nullable=False),
        sa.Column('purchased_qty', sa.Numeric(12, 3), nullable=False),
        sa.Column('purchased_uom', sa.String(length=32), nullable=False),
        sa.Column('actual_weight_kg', sa.Numeric(12, 3), nullable=True),
        sa.Column('unit_cost', sa.Numeric(12, 2), nullable=True),
        sa.Column('result_status', result_status, nullable=False),
        sa.Column('recorded_by', sa.String(length=64), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('note', sa.Text(), nullable=True),
    )
    op.create_index('idx_purchase_results_allocation_id', 'purchase_results', ['allocation_id'])
    op.create_index('idx_purchase_results_result_status', 'purchase_results', ['result_status'])

    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('invoice_no', sa.String(length=64), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('invoice_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('subtotal', sa.Numeric(12, 2), nullable=False),
        sa.Column('tax_total', sa.Numeric(12, 2), nullable=False),
        sa.Column('grand_total', sa.Numeric(12, 2), nullable=False),
        sa.Column('status', invoice_status, nullable=False),
        sa.Column('created_by', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('invoice_no'),
    )

    op.create_table(
        'invoice_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('invoice_id', sa.Integer(), sa.ForeignKey('invoices.id'), nullable=False),
        sa.Column('order_item_id', sa.Integer(), sa.ForeignKey('order_items.id'), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('qty_display', sa.Numeric(12, 3), nullable=False),
        sa.Column('uom_display', sa.String(length=32), nullable=False),
        sa.Column('weight_kg', sa.Numeric(12, 3), nullable=True),
        sa.Column('unit_price', sa.Numeric(12, 2), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('tax_code', sa.String(length=32), nullable=False),
        sa.Column('tax_amount', sa.Numeric(12, 2), nullable=False),
    )

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('entity_type', sa.String(length=64), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', audit_action, nullable=False),
        sa.Column('before_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('after_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reason_code', sa.String(length=64), nullable=True),
        sa.Column('changed_by', sa.String(length=64), nullable=False),
        sa.Column('changed_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('id', 'entity_type', name='uq_audit_id_entity'),
    )
    op.create_index('idx_audit_entity', 'audit_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_audit_changed_at', 'audit_logs', ['changed_at'])


def downgrade() -> None:
    op.drop_index('idx_audit_changed_at', table_name='audit_logs')
    op.drop_index('idx_audit_entity', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_table('invoice_items')
    op.drop_table('invoices')
    op.drop_index('idx_purchase_results_result_status', table_name='purchase_results')
    op.drop_index('idx_purchase_results_allocation_id', table_name='purchase_results')
    op.drop_table('purchase_results')
    op.drop_index('idx_allocations_manual_override', table_name='supplier_allocations')
    op.drop_index('idx_allocations_final_supplier_id', table_name='supplier_allocations')
    op.drop_index('idx_allocations_order_item_id', table_name='supplier_allocations')
    op.drop_table('supplier_allocations')
    op.drop_index('idx_order_items_line_status', table_name='order_items')
    op.drop_index('idx_order_items_product_id', table_name='order_items')
    op.drop_index('idx_order_items_order_id', table_name='order_items')
    op.drop_table('order_items')
    op.drop_index('idx_orders_order_datetime', table_name='orders')
    op.drop_index('idx_orders_status', table_name='orders')
    op.drop_index('idx_orders_customer_id', table_name='orders')
    op.drop_table('orders')
    op.drop_index('idx_products_active', table_name='products')
    op.drop_index('idx_products_sku', table_name='products')
    op.drop_table('products')

    sa.Enum(name='auditaction').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='invoicestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='resultstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='linestatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='orderstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='pricingbasis').drop(op.get_bind(), checkfirst=True)
