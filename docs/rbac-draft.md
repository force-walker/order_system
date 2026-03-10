# RBAC Draft (MVP)

Updated: 2026-03-10

## Roles
- **Admin**: Full access
- **受注入力者 (Order Entry)**: Order entry + invoicing
- **発注者 (Buyer)**: Allocation + purchasing operations
- **仕入先 (Supplier)**: Purchase result registration (limited)
- **販売先 (Customer)**: Delivery receipt confirmation (limited)

Legend:
- ✅ Allowed
- 🔒 Not allowed
- ⚠️ Conditional / limited

---

## Permission Matrix (Function × Role)

- **Order create/edit (`orders`, `order_items`)**
  - Admin: ✅
  - 受注入力者: ✅
  - 発注者: ⚠️ (view + limited correction only after confirm)
  - 仕入先: 🔒
  - 販売先: 🔒

- **Order confirm (`new -> confirmed`)**
  - Admin: ✅
  - 受注入力者: ✅
  - 発注者: ⚠️ (allowed when delegated)
  - 仕入先: 🔒
  - 販売先: 🔒

- **Allocation run auto**
  - Admin: ✅
  - 受注入力者: 🔒
  - 発注者: ✅
  - 仕入先: 🔒
  - 販売先: 🔒

- **Allocation override / split-line / confirm**
  - Admin: ✅
  - 受注入力者: 🔒
  - 発注者: ✅
  - 仕入先: 🔒
  - 販売先: 🔒

- **Purchase result registration (`purchase_results`)**
  - Admin: ✅
  - 受注入力者: 🔒
  - 発注者: ✅
  - 仕入先: ✅ (only own assigned lines)
  - 販売先: 🔒

- **Update final purchase unit cost (`final_unit_cost`)**
  - Admin: ✅
  - 受注入力者: 🔒
  - 発注者: ✅
  - 仕入先: ⚠️ (propose/update own lines if enabled)
  - 販売先: 🔒

- **Delivery receipt confirmation (`shipped -> delivered`)**
  - Admin: ✅
  - 受注入力者: ⚠️ (manual fallback only)
  - 発注者: ✅
  - 仕入先: 🔒
  - 販売先: ✅ (own orders only)

- **Invoice create/finalize (`delivered -> invoiced`)**
  - Admin: ✅
  - 受注入力者: ✅
  - 発注者: ⚠️ (view only by default)
  - 仕入先: 🔒
  - 販売先: 🔒

- **Cancel (`* -> cancelled`)**
  - Admin: ✅
  - 受注入力者: ⚠️ (new/confirmed only)
  - 発注者: ⚠️ (confirmed/purchasing/shipped under policy)
  - 仕入先: 🔒
  - 販売先: 🔒

- **Audit log view/export**
  - Admin: ✅
  - 受注入力者: ⚠️ (own operation scope)
  - 発注者: ⚠️ (procurement scope)
  - 仕入先: 🔒
  - 販売先: 🔒

---

## Guardrails
- Any override/cancel/status rollback-like action requires:
  - reason code
  - actor id
  - timestamp
  - audit log before/after
- Supplier/Customer access must be row-scoped (tenant/order scoped).
- No role except Admin can bypass hard-stop invoice validations.

---

## Open points to finalize
- Whether 受注入力者 can change `delivery_date` after `confirmed`
- Whether 仕入先 can edit `final_unit_cost` directly or suggestion-only
- Whether 発注者 can finalize invoice in emergency mode
