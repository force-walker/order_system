"""align core schema to MVP v2

Revision ID: 2026031701
Revises: 2026030302
Create Date: 2026-03-17 23:05:00
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026031701'
down_revision = '2026030302'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- pricing basis enum migration ---
    op.execute("ALTER TYPE pricingbasis RENAME TO pricingbasis_old")
    op.execute("CREATE TYPE pricingbasis AS ENUM ('uom_count', 'uom_kg')")

    op.execute(
        """
        ALTER TABLE products
        ALTER COLUMN pricing_basis_default TYPE pricingbasis
        USING (
          CASE pricing_basis_default::text
            WHEN 'per_order_uom' THEN 'uom_count'
            WHEN 'per_kg' THEN 'uom_kg'
            ELSE 'uom_count'
          END
        )::pricingbasis
        """
    )
    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN pricing_basis TYPE pricingbasis
        USING (
          CASE pricing_basis::text
            WHEN 'per_order_uom' THEN 'uom_count'
            WHEN 'per_kg' THEN 'uom_kg'
            ELSE 'uom_count'
          END
        )::pricingbasis
        """
    )

    # rename columns for dual-UOM naming
    op.alter_column('order_items', 'ordered_uom', new_column_name='order_uom_type')
    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN order_uom_type TYPE pricingbasis
        USING (
          CASE order_uom_type::text
            WHEN 'per_order_uom' THEN 'uom_count'
            WHEN 'per_kg' THEN 'uom_kg'
            ELSE 'uom_count'
          END
        )::pricingbasis
        """
    )
    op.alter_column('order_items', 'unit_price_order_uom', new_column_name='unit_price_uom_count')
    op.alter_column('order_items', 'unit_price_per_kg', new_column_name='unit_price_uom_kg')

    # remove old enum only after all columns migrated
    op.execute("DROP TYPE pricingbasis_old")

    # --- order status enum migration ---
    op.execute("ALTER TYPE orderstatus RENAME TO orderstatus_old")
    op.execute(
        "CREATE TYPE orderstatus AS ENUM ('new','confirmed','allocated','purchased','shipped','invoiced','cancelled')"
    )
    op.execute(
        """
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus
        USING (
          CASE status::text
            WHEN 'new' THEN 'new'
            WHEN 'confirmed' THEN 'confirmed'
            WHEN 'purchasing' THEN 'allocated'
            WHEN 'shipped' THEN 'shipped'
            WHEN 'delivered' THEN 'invoiced'
            WHEN 'completed' THEN 'invoiced'
            WHEN 'cancelled' THEN 'cancelled'
            ELSE 'new'
          END
        )::orderstatus
        """
    )
    op.execute("DROP TYPE orderstatus_old")

    # --- line status enum migration (add shipped) ---
    op.execute("ALTER TYPE linestatus RENAME TO linestatus_old")
    op.execute(
        "CREATE TYPE linestatus AS ENUM ('open','allocated','purchased','shipped','invoiced','cancelled')"
    )
    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN line_status TYPE linestatus
        USING (
          CASE line_status::text
            WHEN 'open' THEN 'open'
            WHEN 'allocated' THEN 'allocated'
            WHEN 'purchased' THEN 'purchased'
            WHEN 'invoiced' THEN 'invoiced'
            WHEN 'cancelled' THEN 'cancelled'
            ELSE 'open'
          END
        )::linestatus
        """
    )
    op.execute("DROP TYPE linestatus_old")

    # orders.delivery_date is required in v2
    op.add_column('orders', sa.Column('delivery_date', sa.Date(), nullable=True))
    op.execute("UPDATE orders SET delivery_date = DATE(order_datetime) WHERE delivery_date IS NULL")
    op.alter_column('orders', 'delivery_date', nullable=False)

    # enforce v2 price-basis rule
    op.create_check_constraint(
        'ck_order_items_price_by_basis',
        'order_items',
        "(pricing_basis = 'uom_count' AND unit_price_uom_count IS NOT NULL) OR (pricing_basis = 'uom_kg' AND unit_price_uom_kg IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint('ck_order_items_price_by_basis', 'order_items', type_='check')
    op.drop_column('orders', 'delivery_date')

    op.execute("ALTER TYPE linestatus RENAME TO linestatus_new")
    op.execute("CREATE TYPE linestatus AS ENUM ('open','allocated','purchased','invoiced','cancelled')")
    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN line_status TYPE linestatus
        USING (
          CASE line_status::text
            WHEN 'open' THEN 'open'
            WHEN 'allocated' THEN 'allocated'
            WHEN 'purchased' THEN 'purchased'
            WHEN 'invoiced' THEN 'invoiced'
            WHEN 'cancelled' THEN 'cancelled'
            WHEN 'shipped' THEN 'purchased'
            ELSE 'open'
          END
        )::linestatus
        """
    )
    op.execute("DROP TYPE linestatus_new")

    op.execute("ALTER TYPE orderstatus RENAME TO orderstatus_new")
    op.execute("CREATE TYPE orderstatus AS ENUM ('new','confirmed','purchasing','shipped','delivered','completed','cancelled')")
    op.execute(
        """
        ALTER TABLE orders
        ALTER COLUMN status TYPE orderstatus
        USING (
          CASE status::text
            WHEN 'new' THEN 'new'
            WHEN 'confirmed' THEN 'confirmed'
            WHEN 'allocated' THEN 'purchasing'
            WHEN 'purchased' THEN 'purchasing'
            WHEN 'shipped' THEN 'shipped'
            WHEN 'invoiced' THEN 'completed'
            WHEN 'cancelled' THEN 'cancelled'
            ELSE 'new'
          END
        )::orderstatus
        """
    )
    op.execute("DROP TYPE orderstatus_new")

    op.alter_column('order_items', 'unit_price_uom_kg', new_column_name='unit_price_per_kg')
    op.alter_column('order_items', 'unit_price_uom_count', new_column_name='unit_price_order_uom')

    op.execute("ALTER TYPE pricingbasis RENAME TO pricingbasis_new")
    op.execute("CREATE TYPE pricingbasis AS ENUM ('per_order_uom', 'per_kg')")

    op.execute(
        """
        ALTER TABLE products
        ALTER COLUMN pricing_basis_default TYPE pricingbasis
        USING (
          CASE pricing_basis_default::text
            WHEN 'uom_count' THEN 'per_order_uom'
            WHEN 'uom_kg' THEN 'per_kg'
            ELSE 'per_order_uom'
          END
        )::pricingbasis
        """
    )

    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN pricing_basis TYPE pricingbasis
        USING (
          CASE pricing_basis::text
            WHEN 'uom_count' THEN 'per_order_uom'
            WHEN 'uom_kg' THEN 'per_kg'
            ELSE 'per_order_uom'
          END
        )::pricingbasis
        """
    )

    op.execute(
        """
        ALTER TABLE order_items
        ALTER COLUMN order_uom_type TYPE VARCHAR(32)
        USING (
          CASE order_uom_type::text
            WHEN 'uom_count' THEN 'per_order_uom'
            WHEN 'uom_kg' THEN 'per_kg'
            ELSE 'per_order_uom'
          END
        )
        """
    )
    op.alter_column('order_items', 'order_uom_type', new_column_name='ordered_uom')

    op.execute("DROP TYPE pricingbasis_new")
