# DB Draft: Dual-UOM + Catch-Weight Support

## Goal
Support operations where orders are entered in one unit (e.g., piece) while purchasing/invoicing are finalized in another (e.g., kg actual weight).

---

## Core Concepts

- **Order UOM**: Unit used by order-entry staff (`piece`, `box`, etc.)
- **Purchase UOM**: Unit used for supplier purchase (`kg`, `case`, etc.)
- **Invoice UOM / Basis**: Unit and logic used for billing customer (`per_kg` for catch-weight)
- **Catch-weight item**: Item sold by actual measured weight at fulfillment time

---

## Proposed Tables / Key Columns

## 1) `products`
Master rules per item.

- `id` (PK)
- `sku` (unique)
- `name`
- `order_uom` (varchar)
- `purchase_uom` (varchar)
- `invoice_uom` (varchar)
- `is_catch_weight` (boolean, default false)
- `weight_capture_required` (boolean, default false)
- `pricing_basis_default` (`per_order_uom` | `per_kg`)
- `rounding_weight_scale` (int, e.g., 3)
- `rounding_amount_scale` (int, e.g., 0 for JPY)
- `active` (boolean)
- `created_at`, `updated_at`

Indexes:
- `idx_products_sku`
- `idx_products_active`

## 2) `orders`
Order header.

- `id` (PK)
- `order_no` (unique)
- `customer_id` (FK)
- `order_datetime`
- `delivery_type` (`delivery` | `pickup`)
- `delivery_address_snapshot` (text/json)
- `payment_method` (nullable)
- `payment_status` (nullable)
- `status` (`new` | `confirmed` | `purchasing` | `shipped` | `delivered` | `completed` | `cancelled`)
- `note` (nullable)
- `created_by`, `created_at`, `updated_at`

Indexes:
- `idx_orders_customer_id`
- `idx_orders_status`
- `idx_orders_order_datetime`

## 3) `order_items`
Line-level unit/weight/price details.

- `id` (PK)
- `order_id` (FK)
- `product_id` (FK)
- `ordered_qty` (numeric(12,3))
- `ordered_uom` (varchar)
- `estimated_weight_kg` (numeric(12,3), nullable)
- `actual_weight_kg` (numeric(12,3), nullable)
- `pricing_basis` (`per_order_uom` | `per_kg`)
- `unit_price_order_uom` (numeric(12,2), nullable)
- `unit_price_per_kg` (numeric(12,2), nullable)
- `discount_amount` (numeric(12,2), default 0)
- `tax_code` (varchar)
- `line_subtotal` (numeric(12,2), nullable or computed)
- `line_tax` (numeric(12,2), nullable or computed)
- `line_total` (numeric(12,2), nullable or computed)
- `line_status` (`open` | `allocated` | `purchased` | `invoiced` | `cancelled`)
- `created_at`, `updated_at`

Validation rules:
- `ordered_qty > 0`
- If `pricing_basis = per_kg` then `unit_price_per_kg` required
- If `pricing_basis = per_order_uom` then `unit_price_order_uom` required

Indexes:
- `idx_order_items_order_id`
- `idx_order_items_product_id`
- `idx_order_items_line_status`

## 4) `supplier_allocations`
Auto-suggest + manual override trail.

- `id` (PK)
- `order_item_id` (FK)
- `suggested_supplier_id` (FK)
- `final_supplier_id` (FK)
- `suggested_qty` (numeric(12,3))
- `suggested_uom` (varchar)
- `final_qty` (numeric(12,3))
- `final_uom` (varchar)
- `is_manual_override` (boolean, default false)
- `override_reason_code` (varchar, nullable)
- `override_note` (text, nullable)
- `overridden_by` (FK user, nullable)
- `overridden_at` (timestamp, nullable)
- `created_at`, `updated_at`

Indexes:
- `idx_allocations_order_item_id`
- `idx_allocations_final_supplier_id`
- `idx_allocations_manual_override`

## 5) `purchase_results`
Record actual buying outcome.

- `id` (PK)
- `allocation_id` (FK)
- `purchased_qty` (numeric(12,3))
- `purchased_uom` (varchar)
- `actual_weight_kg` (numeric(12,3), nullable)
- `unit_cost` (numeric(12,2), nullable)
- `result_status` (`full` | `partial` | `failed` | `substitute`)
- `recorded_by` (FK user)
- `recorded_at` (timestamp)
- `note` (nullable)

Indexes:
- `idx_purchase_results_allocation_id`
- `idx_purchase_results_result_status`

## 6) `invoices` / `invoice_items`
Billing output.

`invoices`:
- `id` (PK)
- `invoice_no` (unique)
- `customer_id` (FK)
- `invoice_date`
- `due_date` (nullable)
- `subtotal`, `tax_total`, `grand_total`
- `status` (`draft` | `finalized` | `sent` | `paid` | `cancelled`)
- `created_by`, `created_at`, `updated_at`

`invoice_items`:
- `id` (PK)
- `invoice_id` (FK)
- `order_item_id` (FK)
- `description`
- `qty_display` (numeric)
- `uom_display` (varchar)
- `weight_kg` (nullable)
- `unit_price`
- `amount`
- `tax_code`, `tax_amount`

## 7) `audit_logs`
Required for critical/no-error operations.

- `id` (PK)
- `entity_type` (e.g., `allocation`, `order_item`, `invoice`)
- `entity_id`
- `action` (`create` | `update` | `status_change` | `override`)
- `before_json` (jsonb)
- `after_json` (jsonb)
- `reason_code` (nullable)
- `changed_by`
- `changed_at`

Indexes:
- `idx_audit_entity`
- `idx_audit_changed_at`

---

## Notes for MVP
- Keep all quantity/weight fields as `numeric`, not float.
- Keep invoice totals server-side authoritative.
- Do not allow invoice finalization if catch-weight item is missing `actual_weight_kg`.
- Keep a cutoff batch id (future table `operation_batches`) for nightly workflow traceability.
