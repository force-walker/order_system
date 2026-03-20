import json
from pathlib import Path

import yaml
from fastapi.testclient import TestClient

from app.main import app


def main() -> int:
    docs_path = Path(__file__).resolve().parents[1] / 'docs' / 'openapi-mvp-skeleton-draft.yaml'
    if not docs_path.exists():
        print(f'[openapi-sync] docs file not found: {docs_path}')
        return 1

    docs = yaml.safe_load(docs_path.read_text(encoding='utf-8'))
    docs_paths = set((docs.get('paths') or {}).keys())

    client = TestClient(app)
    runtime = client.get('/openapi.json').json()
    runtime_paths = set((runtime.get('paths') or {}).keys())

    missing_in_docs = sorted(runtime_paths - docs_paths)
    extra_in_docs = sorted(docs_paths - runtime_paths)

    if missing_in_docs or extra_in_docs:
        print('[openapi-sync] mismatch detected')
        if missing_in_docs:
            print('  Missing in docs:')
            for p in missing_in_docs:
                print(f'    - {p}')
        if extra_in_docs:
            print('  Extra in docs (not in runtime):')
            for p in extra_in_docs:
                print(f'    - {p}')
        return 1

    print(f'[openapi-sync] OK: {len(runtime_paths)} paths aligned')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
