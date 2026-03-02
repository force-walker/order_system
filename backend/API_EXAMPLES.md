# API Examples (MVP)

## 1) Create product

`POST /api/products`

```json
{
  "sku": "FISH-A",
  "name": "Fish A",
  "order_uom": "piece",
  "purchase_uom": "kg",
  "invoice_uom": "kg",
  "is_catch_weight": true,
  "weight_capture_required": true,
  "pricing_basis_default": "per_kg"
}
```

## 2) Create order

`POST /api/orders`

```json
{
  "order_no": "ORD-2001",
  "customer_id": 1,
  "order_datetime": "2026-03-03T02:00:00Z",
  "delivery_type": "delivery",
  "created_by": "ikoji",
  "items": [
    {
      "product_id": 1,
      "ordered_qty": 1,
      "ordered_uom": "piece",
      "actual_weight_kg": 2.43,
      "pricing_basis": "per_kg",
      "unit_price_per_kg": 3200,
      "discount_amount": 0,
      "tax_code": "standard"
    }
  ]
}
```

## 3) Run auto allocation

`POST /api/allocations/run-auto?default_supplier_id=1`

## 4) Override allocation

`PATCH /api/allocations/{allocation_id}/override`

```json
{
  "final_supplier_id": 2,
  "final_qty": 1,
  "final_uom": "piece",
  "override_reason_code": "better_price",
  "override_note": "spot deal",
  "overridden_by": "ikoji"
}
```

## 5) Create invoice

`POST /api/invoices`

```json
{
  "order_id": 1,
  "invoice_no": "INV-1001",
  "invoice_date": "2026-03-03",
  "created_by": "ikoji"
}
```

## 6) Finalize invoice

`POST /api/invoices/{invoice_id}/finalize`
