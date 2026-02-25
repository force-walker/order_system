# Allocation Flow Draft: Auto Split + Manual Override

## Goal
Speed up purchasing with automatic supplier allocation, while guaranteeing human control for real-world constraints.

---

## Actors
- **Order Entry Staff (受注担当)**
- **Buyer/Purchasing Staff (買い付け担当)**
- **Supervisor (optional unlock/approval)**

---

## End-to-End Flow

1. **Cutoff / Batch Creation**
   - System creates a purchasing batch at cutoff time (e.g., 01:00).
   - Includes all eligible order lines in `confirmed` state.

2. **Auto Allocation Execution**
   - Engine applies mapping rules:
     - Product→Preferred supplier
     - Customer-specific supplier override (if any)
     - Time/day constraints
     - Minimum lot constraints (future)
   - Produces `suggested_supplier`, `suggested_qty`.

3. **Review Screen**
   - Three views:
     - By Supplier (for purchase dispatch)
     - By Customer (for order consistency)
     - By Product (for consolidation)
   - Warning badges:
     - unassigned supplier
     - quantity mismatch
     - catch-weight item with no planned handling note

4. **Manual Adjustment**
   - Buyer can:
     - Change supplier
     - Split one line into multiple suppliers
     - Adjust final qty/uom
   - System requires:
     - `override_reason_code`
     - optional note
   - All edits are audit-logged.

5. **Validation Gate**
   - Block confirm if:
     - unassigned lines remain
     - invalid qty (<= 0)
     - required fields missing
   - Show summary totals by supplier/product/customer.

6. **Confirm & Lock Version**
   - Save as versioned allocation set (`v1 auto`, `v2 adjusted`, ...)
   - Batch status → `ready_to_purchase`
   - Generate printable/exportable supplier purchase list.

7. **Purchase Result Registration**
   - Buyer records actual outcomes (`full/partial/failed/substitute`)
   - Catch-weight actuals recorded where needed.

---

## UI Behavior Requirements

## A) Auto Allocation Page
- Button: `Run Auto Allocation`
- Show runtime + count processed
- Show high-level success/failure summary

## B) Allocation Review Grid
Columns (minimum):
- Customer
- Product
- Ordered Qty/UOM
- Suggested Supplier
- Final Supplier (editable)
- Suggested Qty
- Final Qty (editable)
- Manual Override flag
- Reason code

Actions:
- `Change supplier`
- `Split line`
- `Revert to suggested`
- `Bulk set supplier`

## C) Conflict and Warning Panel
- Unassigned lines
- Split lines count
- Catch-weight lines requiring later actual weight

## D) Confirm Dialog (Two-Step)
- Step 1: preview totals
- Step 2: explicit confirm with user name/password/2nd click (MVP: second click)

---

## Suggested Override Reason Codes
- `stockout`
- `better_price`
- `quality_issue`
- `urgent_delivery`
- `customer_request`
- `manual_correction`

---

## Non-Functional Safety
- Every override includes `who/when/why`.
- Version locking after confirm.
- Supervisor unlock (future option).
- Export snapshot to CSV/PDF for fallback operations.
