# Business Rules Decision Table Draft (MVP)

Updated: 2026-03-10

## Goal
Fix priority and approval authority for day-to-day exception decisions.

---

## Decision Priority Table

| Priority | Rule Area | Decision Rule | Default Action | Final Approver |
|---|---|---|---|---|
| 1 | Legal/Invoice consistency | Tax/amount consistency cannot be violated | Block invalid finalize | Admin |
| 2 | Customer agreed terms | Respect agreed delivery/quality terms | Follow customer contract | 受注責任者 |
| 3 | Stockout handling | Apply `stockout_policy` per line/customer | partial/substitute/backorder/cancel | 発注責任者 |
| 4 | Urgent delivery | Allow override/split for deadline protection | `urgent_delivery` override | 発注責任者 |
| 5 | Price exception | Threshold-based approval | <=5% buyer, >5% admin | Admin (threshold exceed) |
| 6 | Split-line operations | Child totals/UOM must match parent | Block if mismatch | 発注責任者 |
| 7 | Catch-weight invoice gate | `actual_weight_kg` required for per_kg lines | Hard-stop without weight | System hard-stop |
| 8 | Cancellation | `invoiced` cancel blocked (MVP) | Cancel with reason where allowed | Admin |

---

## Conflict Resolution Order (fixed)
1. Legal/invoice consistency
2. Customer agreed terms
3. Stockout policy
4. Urgent delivery handling
5. Price optimization

---

## Approval Threshold Rules

- Price exception threshold:
  - If cost delta <= 5% vs target price: Buyer can approve
  - If cost delta > 5%: Admin approval required

- Cancellation authority:
  - `new`, `confirmed`: Order Entry / Buyer (policy-based)
  - `purchasing`, `shipped`, `delivered`: Buyer + Admin
  - `invoiced`: Admin only and default blocked in MVP

---

## Mandatory Audit Fields (for all exception decisions)
- `reason_code`
- `changed_by`
- `changed_at`
- `before_json`
- `after_json`
- `note` (recommended)

---

## Suggested code sets

### override_reason_code
- `stockout`
- `better_price`
- `quality_issue`
- `urgent_delivery`
- `customer_request`
- `manual_correction`

### stockout_policy
- `backorder`
- `substitute`
- `cancel`
- `partial_ok`

### cancel_reason_code
- `customer_cancelled`
- `stockout_unresolved`
- `data_error`
- `duplicate_order`
- `policy_exception`
