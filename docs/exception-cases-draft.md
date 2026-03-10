# Exception Cases Draft (MVP)

Updated: 2026-03-10

## Goal
Define operational exception patterns so users can act consistently and system behavior is deterministic.

---

## Exception Case List

## E1. Partial fulfillment
- Situation: Supplier can fulfill only part of requested qty.
- Inputs:
  - available qty
  - remaining qty
  - customer priority
- Required action:
  - record `result_status=partial`
  - set handling policy (`partial_ok` / `backorder` / `cancel`)
  - notify customer-facing note
- Audit: mandatory

## E2. Supplier stockout
- Situation: Assigned supplier cannot provide item.
- Inputs:
  - stockout confirmation
  - alternative suppliers / lead times
- Required action:
  - manual override or split-line
  - reason code `stockout`
- Audit: mandatory

## E3. Substitute item
- Situation: Original item unavailable, substitute proposed.
- Inputs:
  - substitute sku/spec
  - price delta
  - customer approval flag
- Required action:
  - mark `result_status=substitute`
  - preserve original line reference
- Audit: mandatory

## E4. Catch-weight missing actual weight
- Situation: per_kg line has no `actual_weight_kg` at invoice timing.
- Required action:
  - block invoice finalization
  - route back to purchase result registration
- Audit: automatic block event log

## E5. Post-allocation price change
- Situation: final purchase unit cost differs from assumed value.
- Inputs:
  - final_unit_cost
  - effective timestamp
- Required action:
  - update purchase result with `final_unit_cost`
  - keep previous value in audit
- Audit: mandatory

## E6. Customer-requested urgent change
- Situation: customer changes qty/date after confirmed.
- Inputs:
  - requested delta
  - current allocation/purchase state
- Required action:
  - allow only by role + reason
  - re-run validation gate
- Audit: mandatory

## E7. Cancellation after shipping
- Situation: cancel request when shipment already started.
- Required action:
  - admin-only
  - mandatory reason and impact note
  - financial handling handoff (outside MVP)
- Audit: mandatory

## E8. Duplicate order detected
- Situation: same customer/date/items duplicated by mistake.
- Required action:
  - cancel duplicate line/order with reason `duplicate_order`
  - preserve original active order
- Audit: mandatory

---

## Cross-case mandatory fields
- `reason_code`
- `operator`
- `operation_time`
- `before_json` / `after_json`
- `note` (optional but recommended)

---

## Open decisions for next refinement
- Which exception cases require supervisor approval?
- SLA for unresolved partial/backorder cases
- Customer notification ownership (Order Entry vs Buyer)
