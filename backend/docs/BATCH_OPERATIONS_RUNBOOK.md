# Batch Operations Runbook

## Scope
Covers `procurement_regeneration` batch jobs.

## Quick triage
1. Check alerts (`BatchTaskFailureSpike`, `BatchTaskRetryingSpike`).
2. Query latest jobs:
   - `GET /api/v1/batch/jobs?job_type=procurement_regeneration&limit=50`
3. Inspect target task:
   - `GET /api/v1/batch/jobs/{task_id}`

## Decision tree
- status=`completed`:
  - No action.
- status=`retrying`:
  - Wait until retries settle; check infra/DB pressure.
- status=`failed`:
  - Verify `error_message` and related order data.
  - If transient issue likely fixed, run retry endpoint.

## Retry procedure
1. Ensure job is `failed` and retry budget remains.
2. POST `/api/v1/batch/jobs/{task_id}/retry`.
3. Monitor child task via `/api/v1/batch/jobs/{new_task_id}`.

## Safety guards
- Only failed jobs are retryable.
- Only latest attempt in chain is retryable.
- Retry blocked when `retry_count >= max_retries`.
- Per-order lock prevents concurrent regeneration.

## Escalation criteria
- Repeated `RETRY_LIMIT_EXCEEDED` for same order.
- `failed` spikes for >30 minutes.
- Persistent `REGENERATION_IN_PROGRESS` without completion.
