from datetime import datetime
from decimal import Decimal

from app.db.session import SessionLocal
from app.models.entities import PricingBasis, Product, Order, OrderItem, OrderStatus


def run() -> None:
    db = SessionLocal()
    try:
        p1 = Product(
            sku='FISH-A',
            name='Fish A',
            order_uom='piece',
            purchase_uom='kg',
            invoice_uom='kg',
            is_catch_weight=True,
            weight_capture_required=True,
            pricing_basis_default=PricingBasis.per_kg,
        )
        p2 = Product(
            sku='BOX-B',
            name='Box B',
            order_uom='box',
            purchase_uom='box',
            invoice_uom='box',
            is_catch_weight=False,
            pricing_basis_default=PricingBasis.per_order_uom,
        )
        db.add_all([p1, p2])
        db.flush()

        order = Order(
            order_no='ORD-1001',
            customer_id=1,
            order_datetime=datetime.utcnow(),
            delivery_type='delivery',
            status=OrderStatus.confirmed,
            created_by='seed',
        )
        db.add(order)
        db.flush()

        db.add_all([
            OrderItem(
                order_id=order.id,
                product_id=p1.id,
                ordered_qty=Decimal('1'),
                ordered_uom='piece',
                estimated_weight_kg=Decimal('2.500'),
                actual_weight_kg=Decimal('2.430'),
                pricing_basis=PricingBasis.per_kg,
                unit_price_per_kg=Decimal('3200'),
                discount_amount=Decimal('0'),
                tax_code='standard',
            ),
            OrderItem(
                order_id=order.id,
                product_id=p2.id,
                ordered_qty=Decimal('3'),
                ordered_uom='box',
                pricing_basis=PricingBasis.per_order_uom,
                unit_price_order_uom=Decimal('1200'),
                discount_amount=Decimal('100'),
                tax_code='standard',
            ),
        ])

        db.commit()
        print('Seed data inserted: products=2, orders=1')
    finally:
        db.close()


if __name__ == '__main__':
    run()
