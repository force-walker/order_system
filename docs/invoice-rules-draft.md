# Invoice Rules Draft: Mixed Piece + Catch-Weight Billing

## Goal
Support invoices that can contain both fixed-unit items and catch-weight items in the same document, with deterministic and auditable calculations.

---

## Line Calculation Rules

## Rule A: Piece-based pricing
When `pricing_basis = uom_count`

`line_subtotal = ordered_qty × unit_price_order_uom`

Then:
- `line_after_discount = line_subtotal - discount_amount`
- `line_tax = tax(line_after_discount, tax_code)`
- `line_total = line_after_discount + line_tax`

## Rule B: Catch-weight pricing
When `pricing_basis = uom_kg`

`line_subtotal = actual_weight_kg × unit_price_uom_kg`

Then same discount/tax flow as above.

## Rule C: Discount precedence
Discount is applied before tax.

## Rule D: Tax by line
Tax is calculated per line using each line's `tax_code` (not invoice-level blanket tax).

## Rule E: Invoice total
- `invoice_subtotal = Σ line_subtotal_after_discount`
- `invoice_tax_total = Σ line_tax`
- `invoice_grand_total = invoice_subtotal + invoice_tax_total`

---

## Finalization Constraints (Hard Stops)
Cannot finalize invoice if any of the following is true:

1. Catch-weight line missing `actual_weight_kg`
2. Required price missing (`unit_price_uom_kg` or `unit_price_order_uom`)
3. Negative totals after discount
4. Referenced order line is cancelled/invalid
5. Batch/operation state not eligible (if strict workflow enforced)

---

## Display Rules (Customer-Facing)

Invoice header should display a single `delivery_date` (business rule: one invoice does not mix multiple delivery dates).

## Piece-based lines
Show:
- quantity in ordered UOM
- unit price per ordered UOM
- amount

## Catch-weight lines
Show:
- ordered quantity/UOM (optional reference)
- actual weight (kg)
- unit price per kg
- amount based on actual weight

Recommended line description example:
- `Fish A (Order: 1 piece, Actual: 2.43 kg × ¥3,200/kg)`

---

## Currency Rules
- Purchase currency: `JPY`
- Sales/Invoice currency: `HKD`
- FX conversion rule (rate source + timing + rounding) must be fixed before production.

## Rounding Rules
Define globally and keep fixed:

- Weight rounding: e.g., 3 decimals (`0.001 kg`)
- Currency rounding: JPY integer (`0` decimals) unless business rule differs
- Tax rounding policy: per-line floor/round/ceil (must be explicit)

All recalculations must happen server-side with identical rules.

Meaning:
- Client-side values are reference only; server result is authoritative.
- Same input must always return same total/tax result.
- Prevents mismatch across browser/device and improves audit reproducibility.

---

## Auditability Requirements
For any invoice change before finalization:
- Capture before/after values for qty, weight, price, discount, tax
- Capture user and timestamp
- Capture reason when manually edited

On finalization:
- Freeze calculation inputs and totals
- Persist a PDF/render snapshot hash (future enhancement)

---

## Test Cases (Minimum)
1. Piece-only invoice
2. Catch-weight-only invoice
3. Mixed invoice (piece + per-kg)
4. Catch-weight line missing actual weight (must block)
5. Discount + tax rounding edge cases
6. Large quantity precision case
