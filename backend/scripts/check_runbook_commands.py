import re
from pathlib import Path


RUNBOOK_FILES = [
    Path('docs/BATCH_OPERATIONS_RUNBOOK.md'),
    Path('README.md'),
]


CMD_PATTERNS = [
    re.compile(r"/api/v1/batch/procurement-regeneration"),
    re.compile(r"/api/v1/batch/jobs/<task_id>"),
    re.compile(r"/api/v1/batch/jobs\?job_type=procurement_regeneration"),
    re.compile(r"/api/v1/metrics"),
]


def _extract_code_blocks(text: str) -> list[str]:
    blocks = []
    fence = re.compile(r"```(?:bash)?\n(.*?)```", re.S)
    for m in fence.finditer(text):
        blocks.append(m.group(1))
    return blocks


def main() -> int:
    failed = False
    corpus = []

    for rel in RUNBOOK_FILES:
        if not rel.exists():
            print(f"[runbook-check] missing file: {rel}")
            failed = True
            continue

        text = rel.read_text(encoding='utf-8')
        blocks = _extract_code_blocks(text)
        corpus.append("\n".join(blocks))

    joined = "\n".join(corpus)
    for pat in CMD_PATTERNS:
        if not pat.search(joined):
            print(f"[runbook-check] missing command pattern across runbook docs: {pat.pattern}")
            failed = True

    if failed:
        return 1

    print("[runbook-check] OK: required runbook command patterns are present")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
