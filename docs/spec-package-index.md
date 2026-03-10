# Order Input System — Spec Package (Draft A)

Created: 2026-02-25
Updated: 2026-03-05

## Included Documents

1. `docs/db-dual-uom-draft.md`
   - Dual unit-of-measure data model draft
   - Catch-weight support columns and validations
   - Allocation split-line / target-price / stockout-policy / final unit-cost extensions

2. `docs/allocation-flow-draft.md`
   - Auto supplier allocation flow
   - Manual override workflow and safety controls
   - Unified multi-grid design (By Supplier / By Customer / By Product)

3. `docs/invoice-rules-draft.md`
   - Billing rules for mixed piece + per-kg invoices
   - Finalization constraints and rounding policy

4. `docs/flowchart-stakeholders.md`
   - End-to-end role flow (受注入力者 / 発注者 / 仕入れ先 / 販売先)
   - Role responsibilities and key inputs/outputs

5. `docs/status-transition-draft.md`
   - Lifecycle transition definition
   - MVP terminal status = `invoiced` (`completed` removed)
   - `paid` deferred to future accounting scope

6. `docs/exception-cases-draft.md`
   - Exception scenarios (partial, stockout, substitute, catch-weight blocking, etc.)
   - Required actions and audit requirements

7. `docs/non-functional-requirements-draft.md`
   - Performance/availability/security/audit/backup/operations requirements
   - MVP service quality and operational baselines

8. `docs/rbac-draft.md`
   - Role-based access control matrix (Admin / 受注入力者 / 発注者 / 仕入先 / 販売先)
   - Function-level create/update/confirm/cancel permissions

9. `docs/business-rules-decision-table-draft.md`
   - Decision priority table and final approver mapping
   - Conflict resolution order and approval thresholds

10. `docs/api-authorization-spec-draft.md`
   - Endpoint-level authorization policy by role
   - Scope rules, audit requirements, and auth error semantics

## Scope
This package is draft-level functional specification for MVP planning and implementation handoff.

## Next Recommended Step
- Confirm business rule details:
  - tax rounding policy
  - override reason code list
  - stockout policy code list
  - target price mandatory/optional rule
  - cutoff timing and lock/unlock policy
- Then convert into implementation-ready artifacts:
  - SQL migrations
  - API contract
  - screen wireframes (3-grid unified schema)
