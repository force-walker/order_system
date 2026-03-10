# Status Transition Draft (Order Lifecycle)

Updated: 2026-03-10

## Final status policy (MVP)

Main flow:

`new → confirmed → purchasing → shipped → delivered → invoiced`

Exception flow:

`* → cancelled` (allowed with role/condition controls)

### Notes
- `invoiced` is the terminal status for MVP completion.
- `completed` is removed.
- `paid` is intentionally deferred to a future version (accounting scope).

---

## Transition rules

## 1) `new → confirmed`
- Actor: Order Entry, Admin
- Required:
  - customer + delivery date
  - at least 1 valid order line
  - mandatory pricing basis fields

## 2) `confirmed → purchasing`
- Actor: Buyer, Admin
- Required:
  - allocation run completed
  - no unassigned mandatory lines

## 3) `purchasing → shipped`
- Actor: Buyer, Admin
- Required:
  - purchase result registration started
  - blocking shortages handled by policy (`stockout_policy`)

## 4) `shipped → delivered`
- Actor: Buyer, Admin
- Required:
  - delivery confirmation (manual or external signal)

## 5) `delivered → invoiced`
- Actor: Billing, Admin
- Required:
  - invoice generated and finalized
  - catch-weight lines have `actual_weight_kg`
  - price/tax validations pass

---

## Cancel rules (`* → cancelled`)

- Allowed from: `new`, `confirmed`, `purchasing`, `shipped`, `delivered`
- Not allowed from: `invoiced` (MVP default hard-stop)
- Required on cancel:
  - cancel reason code
  - actor + timestamp
  - audit log (`before/after`, reason)

Suggested cancel reason codes:
- `customer_cancelled`
- `stockout_unresolved`
- `data_error`
- `duplicate_order`
- `policy_exception`

---

## Audit requirements

Every state change must store:
- who changed status
- when
- from_status / to_status
- reason_code (required for cancel, reopen-like operations)
- optional note

---

## Future extension (vNext)

When accounting is in scope, add:
- `paid` status
- `invoiced → paid` transition conditions
- payment reconciliation + lock policy
