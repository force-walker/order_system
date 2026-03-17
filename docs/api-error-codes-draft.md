# API Error Codes Draft (MVP)

Updated: 2026-03-16
Status: Draft (implementation-ready baseline)

## 1. Standard Error Response

```json
{
  "error_code": "VERSION_CONFLICT",
  "message": "Record has been updated by another user. Please reload and retry.",
  "field": "version",
  "resource": "invoice",
  "resource_id": "inv_123",
  "detail": {
    "current_version": 18
  },
  "trace_id": "req_..."
}
```

Required fields:
- `error_code` (string, stable)
- `message` (string, human readable)

Optional fields:
- `field` (string)
- `resource` (string)
- `resource_id` (string|number)
- `detail` (object)
- `trace_id` (string)

---

## 2. HTTP Status Usage Policy

- `400 Bad Request`: malformed request / missing required control fields
- `401 Unauthorized`: missing/invalid auth
- `403 Forbidden`: role/scope not allowed
- `404 Not Found`: target not found in accessible scope
- `409 Conflict`: state/version/lock conflict
- `422 Unprocessable Entity`: business validation failure

---

## 3. Error Code Catalog

## 3.1 400 Bad Request

- `INVALID_REQUEST_FORMAT`
  - JSON/body shape invalid
- `MISSING_REQUIRED_FIELD`
  - required field missing
- `INVALID_REASON_CODE`
  - reason code not in allowed set
- `INVALID_DATE_FORMAT`
  - date/datetime format invalid

## 3.2 401 Unauthorized

- `AUTH_REQUIRED`
- `AUTH_INVALID_TOKEN`
- `AUTH_EXPIRED_TOKEN`

## 3.3 403 Forbidden

- `PERMISSION_DENIED`
  - role not allowed for endpoint
- `SCOPE_FORBIDDEN`
  - resource out of actor scope (e.g. supplier tries non-assigned line)
- `LOCKED_PERIOD_FORBIDDEN`
  - invoice is locked (after lock date) and actor not admin-unlocked

## 3.4 404 Not Found

- `RESOURCE_NOT_FOUND`
- `ORDER_NOT_FOUND`
- `INVOICE_NOT_FOUND`
- `ALLOCATION_NOT_FOUND`

## 3.5 409 Conflict

- `VERSION_CONFLICT`
  - optimistic lock mismatch
- `STATUS_TRANSITION_CONFLICT`
  - invalid transition for current status
- `STATUS_NO_TARGET_LINES`
  - no eligible lines found for the requested transition
- `INVOICE_LOCKED`
  - update attempted after lock date
- `DUPLICATE_INVOICE_NO`
  - unique conflict on invoice_no
- `REGENERATION_IN_PROGRESS`
  - procurement regeneration already running on same order

## 3.6 422 Unprocessable Entity

- `VALIDATION_FAILED`
  - generic field/business validation failure
- `INVALID_BILLABLE_QTY`
  - billable qty <= 0 or exceeds uninvoiced remainder
- `MISSING_ACTUAL_WEIGHT`
  - catch-weight invoice line missing `actual_weight_kg`
- `MISSING_REQUIRED_UNIT_PRICE`
  - required pricing absent
- `INVOICEABLE_FLAG_FALSE_INCLUDED`
  - selected lines include `invoiceable_flag=false`
- `RESULT_STATUS_NOT_FILLED_INCLUDED`
  - selected lines include `result_status=not_filled`
- `TAX_MISMATCH`
  - tax not equal to `floor(total_amount_pretax × tax_rate)`
- `TOTAL_MISMATCH`
  - total mismatch with subtotal + tax
- `NEGATIVE_AMOUNT_NOT_ALLOWED`
  - negative monetary value detected
- `UNLOCK_REASON_REQUIRED`
  - unlock endpoint called without required reason_code
- `SHORTAGE_NOTE_REQUIRED`
  - `shortage_reason_code=manual_adjustment` without shortage_note

---

## 4. Endpoint-specific Mapping (MVP Priority)

## Invoice finalize (`POST /api/invoices/{id}/finalize`)
- `400 MISSING_REQUIRED_FIELD` (request controls missing)
- `403 PERMISSION_DENIED`
- `404 INVOICE_NOT_FOUND`
- `409 VERSION_CONFLICT`
- `409 INVOICE_LOCKED`
- `422 INVALID_BILLABLE_QTY`
- `422 MISSING_ACTUAL_WEIGHT`
- `422 MISSING_REQUIRED_UNIT_PRICE`
- `422 INVOICEABLE_FLAG_FALSE_INCLUDED`
- `422 RESULT_STATUS_NOT_FILLED_INCLUDED`
- `422 TAX_MISMATCH`
- `422 TOTAL_MISMATCH`
- `422 NEGATIVE_AMOUNT_NOT_ALLOWED`

## Invoice reset-to-draft (`POST /api/invoices/{id}/reset-to-draft`)
- `403 PERMISSION_DENIED` (Admin only)
- `404 INVOICE_NOT_FOUND`
- `409 VERSION_CONFLICT`
- `409 STATUS_TRANSITION_CONFLICT` (not finalized)
- `422 UNLOCK_REASON_REQUIRED` (if reason missing)
- `400 INVALID_REASON_CODE` (reason out of set)

## Allocation override / split
- `403 PERMISSION_DENIED`
- `404 ALLOCATION_NOT_FOUND`
- `409 VERSION_CONFLICT`
- `422 VALIDATION_FAILED` (sum mismatch/UOM mismatch/etc)

## Procurement regeneration
- `403 PERMISSION_DENIED`
- `404 ORDER_NOT_FOUND`
- `409 REGENERATION_IN_PROGRESS`
- `409 VERSION_CONFLICT`

## Order bulk transition (user-triggered)
- `403 PERMISSION_DENIED`
- `404 ORDER_NOT_FOUND`
- `409 STATUS_TRANSITION_CONFLICT`
- `409 STATUS_NO_TARGET_LINES`

---

## 5. Message Style Guide

- `message` should be user-actionable and short.
- Never expose internal SQL/stack traces to clients.
- Use `trace_id` for backend troubleshooting.

Example messages:
- `VERSION_CONFLICT`: "他ユーザー更新あり。最新を再読込して再実行してください。"
- `INVOICE_LOCKED`: "この請求書はロック期間を過ぎているため更新できません。"
- `DUPLICATE_INVOICE_NO`: "請求書番号が重複しました。再試行してください。"

---

## 6. Test Checklist (for UAT/QA)

- Concurrent update returns `409 VERSION_CONFLICT`
- Duplicate invoice_no attempt returns `409 DUPLICATE_INVOICE_NO`
- Locked invoice update returns `409 INVOICE_LOCKED`
- Missing catch-weight actual weight returns `422 MISSING_ACTUAL_WEIGHT`
- Tax mismatch returns `422 TAX_MISMATCH`
- Unauthorized role returns `403 PERMISSION_DENIED`
