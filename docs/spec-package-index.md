# Order Input System — Spec Package (Draft A)

Created: 2026-02-25

## Included Documents

1. `docs/db-dual-uom-draft.md`
   - Dual unit-of-measure data model draft
   - Catch-weight support columns and validations

2. `docs/allocation-flow-draft.md`
   - Auto supplier allocation flow
   - Manual override workflow and safety controls

3. `docs/invoice-rules-draft.md`
   - Billing rules for mixed piece + per-kg invoices
   - Finalization constraints and rounding policy

## Scope
This package is draft-level functional specification for MVP planning and implementation handoff.

## Next Recommended Step
- Confirm business rule details:
  - tax rounding policy
  - override reason code list
  - cutoff timing and lock/unlock policy
- Then convert into implementation-ready artifacts:
  - SQL migrations
  - API contract
  - Screen wireframes
