import re
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from app.main import app


CRITICAL_SCHEMA_REQUIRED = {
    'JobEnqueueResponse': {'task_id', 'status'},
    'JobStatusResponse': {'task_id', 'status'},
    'ErrorResponse': {'code', 'message'},
}


def _load_yaml(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding='utf-8'))


def _collect_runtime_openapi() -> dict:
    client = TestClient(app)
    return client.get('/openapi.json').json()


def _collect_runtime_error_codes(app_dir: Path) -> set[str]:
    code_re = re.compile(r"api_error\(\s*\d+\s*,\s*['\"]([^'\"]+)['\"]")
    codes: set[str] = set()
    for py in app_dir.rglob('*.py'):
        text = py.read_text(encoding='utf-8')
        codes.update(code_re.findall(text))
    return codes


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    backend_root = Path(__file__).resolve().parents[1]

    docs_openapi_path = repo_root / 'docs' / 'openapi-mvp-skeleton-draft.yaml'
    docs_error_path = repo_root / 'docs' / 'openapi-error-components-draft.yaml'

    if not docs_openapi_path.exists() or not docs_error_path.exists():
        print('[openapi-sync] docs files are missing')
        return 1

    docs_openapi = _load_yaml(docs_openapi_path)
    docs_error = _load_yaml(docs_error_path)
    runtime = _collect_runtime_openapi()

    docs_paths = set((docs_openapi.get('paths') or {}).keys())
    runtime_paths = set((runtime.get('paths') or {}).keys())

    missing_in_docs = sorted(runtime_paths - docs_paths)
    extra_in_docs = sorted(docs_paths - runtime_paths)

    failed = False

    if missing_in_docs or extra_in_docs:
        failed = True
        print('[openapi-sync] path mismatch detected')
        if missing_in_docs:
            print('  Missing in docs:')
            for p in missing_in_docs:
                print(f'    - {p}')
        if extra_in_docs:
            print('  Extra in docs (not in runtime):')
            for p in extra_in_docs:
                print(f'    - {p}')

    runtime_schemas = (runtime.get('components') or {}).get('schemas') or {}
    docs_schemas = (docs_openapi.get('components') or {}).get('schemas') or {}
    docs_error_schemas = (docs_error.get('components') or {}).get('schemas') or {}

    # Schema required fields checks.
    for schema_name, required_fields in CRITICAL_SCHEMA_REQUIRED.items():
        if schema_name == 'ErrorResponse':
            source = docs_error_schemas.get(schema_name) or docs_schemas.get(schema_name) or {}
            required = set(source.get('required') or [])
            if not required_fields.issubset(required):
                failed = True
                print(
                    f"[openapi-sync] schema required mismatch ({schema_name}): "
                    f"expected at least {sorted(required_fields)}, got {sorted(required)}"
                )
            continue

        docs_schema = docs_schemas.get(schema_name) or {}
        runtime_schema = runtime_schemas.get(schema_name) or {}

        if not docs_schema:
            failed = True
            print(f'[openapi-sync] docs missing schema: {schema_name}')
            continue
        if not runtime_schema:
            failed = True
            print(f'[openapi-sync] runtime missing schema: {schema_name}')
            continue

        docs_required = set(docs_schema.get('required') or [])
        runtime_required = set(runtime_schema.get('required') or [])

        if docs_required != runtime_required:
            failed = True
            print(
                f"[openapi-sync] schema required mismatch ({schema_name}): "
                f"docs={sorted(docs_required)} runtime={sorted(runtime_required)}"
            )

        if not required_fields.issubset(docs_required):
            failed = True
            print(
                f"[openapi-sync] schema missing critical required fields ({schema_name}): "
                f"required={sorted(required_fields)} docs={sorted(docs_required)}"
            )

    # Error code sync: every runtime api_error code should exist in docs enum.
    runtime_codes = _collect_runtime_error_codes(backend_root / 'app')
    docs_error_enum = set(
        (((docs_error_schemas.get('ErrorResponse') or {}).get('properties') or {}).get('code') or {}).get('enum') or []
    )

    missing_error_codes = sorted(runtime_codes - docs_error_enum)
    if missing_error_codes:
        failed = True
        print('[openapi-sync] error code mismatch: codes used in runtime but missing in docs enum')
        for c in missing_error_codes:
            print(f'  - {c}')

    if failed:
        return 1

    print(
        f"[openapi-sync] OK: paths={len(runtime_paths)} "
        f"schemas_checked={len(CRITICAL_SCHEMA_REQUIRED)} error_codes={len(runtime_codes)}"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
