# Order System Memory (W.M.)

Updated: 2026-03-10 (Asia/Hong_Kong)
Owner: Koji

## Project Snapshot
- Project: Internal order input system (staff-only, web app)
- Priority: Small scale but business-critical, low error tolerance, time-constrained nightly ops

## Operational Flow
1. Evening to ~01:00: receive orders from trading partners; order-entry staff input orders.
2. Next ~1 hour: buyer consolidates all orders and places purchases to suppliers (views needed by customer/product/supplier).
3. Register purchase results.
4. Create invoices.

## Specification Artifacts (Draft A)
- docs/allocation-flow-draft.md
- docs/db-dual-uom-draft.md
- docs/invoice-rules-draft.md
- docs/spec-package-index.md

## Key Design Direction
- Dual UOM + catch-weight support (piece/box vs kg actual)
- Auto allocation with manual override and audit trail
- Mixed invoice rules (per-order-uom + per-kg) with hard-stop validations

## Feedback/Changes from Koji
- Allocation Review Grid should include:
  - 希望価格 (target/preferred price)
  - 欠品の場合の対応 (out-of-stock handling)
  - コメント (comment)
- Purchase Result Registration must include final purchase unit cost input.

## Outstanding Decisions (for Draft B)
- Tax rounding policy (per-line and method: floor/round/ceil)
- Cutoff timing + lock/unlock policy
- Final override reason code set
- Integrations (inventory/payment/notifications/ERP) timing and scope

## Current Status
- Requirements captured at draft level.
- Next step: convert to implementation artifacts (SQL migrations, API contract, screen wireframes).
