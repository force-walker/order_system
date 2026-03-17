# API Error Codes Draft (MVP)

Updated: 2026-03-18
Status: Draft (aligned with current implementation)

## 1. Standard Error Response

```json
{
  "code": "STATUS_NO_TARGET_LINES",
  "message": "no eligible lines"
}
```

Required fields:
- `code` (string, stable)
- `message` (string, human readable)

---

## 2. HTTP Status Usage Policy

- `400 Bad Request`: invalid input / missing required runtime data
- `401 Unauthorized`: missing auth headers
- `403 Forbidden`: role not allowed
- `404 Not Found`: target resource not found
- `409 Conflict`: state transition conflict / lock-state mismatch
- `422 Unprocessable Entity`: enum/pair validation failure

---

## 3. Error Code Catalog (Current)

## 3.1 400 Bad Request

- `ORDER_WEIGHT_REQUIRED`
- `NO_INVOICEABLE_ITEMS`
- `CATCH_WEIGHT_REQUIRED`
- `UNIT_PRICE_UOM_COUNT_REQUIRED`
- `UNIT_PRICE_UOM_KG_REQUIRED`
- `NEGATIVE_INVOICE_TOTAL`
- `ALLOCATION_INVALID`
- `ALLOCATION_INVALID_TARGET_QTY`
- `SPLIT_QTY_MISMATCH`
- `SPLIT_GROUP_MISSING_PARENT`
- `SPLIT_GROUP_MIN_CHILDREN`
- `SPLIT_GROUP_QTY_MISMATCH`
- `SPLIT_GROUP_UOM_MISMATCH`

## 3.2 401 Unauthorized

- `AUTH_REQUIRED`

## 3.3 403 Forbidden

- `FORBIDDEN`

## 3.4 404 Not Found

- `ORDER_NOT_FOUND`
- `INVOICE_NOT_FOUND`
- `ALLOCATION_NOT_FOUND`

## 3.5 409 Conflict

- `ORDER_STATUS_MISMATCH`
- `STATUS_NO_TARGET_LINES`
- `INVOICE_NOT_DRAFT`
- `INVOICE_NOT_FINALIZED`
- `INVOICE_NOT_LOCKED_FINALIZED`

## 3.6 422 Unprocessable Entity

- `INVALID_TRANSITION_PAIR`
- `INVALID_RESET_REASON_CODE`
- `INVALID_UNLOCK_REASON_CODE`

---

## 4. Endpoint-specific Mapping (MVP Priority)

## Order bulk transition (`POST /api/v1/orders/{order_id}/bulk-transition`)
- `403 FORBIDDEN`
- `404 ORDER_NOT_FOUND`
- `409 ORDER_STATUS_MISMATCH`
- `409 STATUS_NO_TARGET_LINES`
- `422 INVALID_TRANSITION_PAIR`

## Invoice finalize (`POST /api/v1/invoices/{invoice_id}/finalize`)
- `403 FORBIDDEN`
- `404 INVOICE_NOT_FOUND`
- `400 NEGATIVE_INVOICE_TOTAL`
- `409 INVOICE_NOT_DRAFT`

## Invoice reset-to-draft (`POST /api/v1/invoices/{invoice_id}/reset-to-draft`)
- `403 FORBIDDEN` (admin / order_entry)
- `404 INVOICE_NOT_FOUND`
- `409 INVOICE_NOT_FINALIZED`
- `422 INVALID_RESET_REASON_CODE`

## Invoice unlock (`POST /api/v1/invoices/{invoice_id}/unlock`)
- `403 FORBIDDEN` (admin only)
- `404 INVOICE_NOT_FOUND`
- `409 INVOICE_NOT_LOCKED_FINALIZED`
- `422 INVALID_UNLOCK_REASON_CODE`

## Allocation override (`PATCH /api/v1/allocations/{allocation_id}/override`)
- `403 FORBIDDEN`
- `404 ALLOCATION_NOT_FOUND`

## Allocation split (`POST /api/v1/allocations/{allocation_id}/split-line`)
- `403 FORBIDDEN`
- `404 ALLOCATION_NOT_FOUND`
- `400 SPLIT_QTY_MISMATCH`
- `400 ALLOCATION_INVALID_TARGET_QTY`

---

## 5. Notes

- This draft reflects **current runtime implementation** (`code/message` payload).
- If we later add richer metadata (`field`, `resource`, `detail`, `trace_id`), update this doc and OpenAPI components together.
