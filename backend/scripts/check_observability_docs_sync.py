import re
from pathlib import Path

import yaml


ALERT_RULES_FILE = Path('alerts/order_system_rules.yml')
RUNBOOK_FILE = Path('docs/BATCH_OPERATIONS_RUNBOOK.md')
README_FILE = Path('README.md')
METRICS_FILE = Path('app/core/metrics.py')


def _extract_alert_names_from_rules(path: Path) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    names: set[str] = set()
    for g in data.get('groups', []):
        for r in g.get('rules', []):
            n = r.get('alert')
            if n:
                names.add(str(n))
    return names


def _extract_alert_names_from_text(text: str) -> set[str]:
    # Matches markdown bullet like - `AlertName`:
    return set(re.findall(r"`([A-Za-z0-9_]+)`", text))


def _extract_metric_names_from_rules(path: Path) -> set[str]:
    data = yaml.safe_load(path.read_text(encoding='utf-8'))
    metrics: set[str] = set()
    metric_re = re.compile(r"\b(order_system_[a-zA-Z0-9_]+)")
    for g in data.get('groups', []):
        for r in g.get('rules', []):
            expr = str(r.get('expr', ''))
            metrics.update(metric_re.findall(expr))
    return metrics


def _extract_metric_names_from_metrics_py(path: Path) -> set[str]:
    text = path.read_text(encoding='utf-8')
    metric_re = re.compile(r"['\"](order_system_[a-zA-Z0-9_]+)['\"]")
    return set(metric_re.findall(text))


def main() -> int:
    failed = False

    for p in [ALERT_RULES_FILE, RUNBOOK_FILE, README_FILE, METRICS_FILE]:
        if not p.exists():
            print(f'[observability-sync] missing file: {p}')
            failed = True

    if failed:
        return 1

    alerts_rules = _extract_alert_names_from_rules(ALERT_RULES_FILE)
    runbook_text = RUNBOOK_FILE.read_text(encoding='utf-8')
    readme_text = README_FILE.read_text(encoding='utf-8')

    alerts_runbook = _extract_alert_names_from_text(runbook_text)
    alerts_readme = _extract_alert_names_from_text(readme_text)

    missing_in_runbook = sorted(alerts_rules - alerts_runbook)
    missing_in_readme = sorted(alerts_rules - alerts_readme)

    if missing_in_runbook:
        failed = True
        print('[observability-sync] alerts missing in runbook:')
        for a in missing_in_runbook:
            print(f'  - {a}')

    if missing_in_readme:
        failed = True
        print('[observability-sync] alerts missing in README:')
        for a in missing_in_readme:
            print(f'  - {a}')

    metrics_in_rules = _extract_metric_names_from_rules(ALERT_RULES_FILE)
    metrics_in_code = _extract_metric_names_from_metrics_py(METRICS_FILE)
    missing_metrics = sorted(metrics_in_rules - metrics_in_code)

    if missing_metrics:
        failed = True
        print('[observability-sync] metrics used in alerts but missing in app/core/metrics.py:')
        for m in missing_metrics:
            print(f'  - {m}')

    if failed:
        return 1

    print(
        f"[observability-sync] OK: alerts={len(alerts_rules)} "
        f"metrics_in_rules={len(metrics_in_rules)} metrics_in_code={len(metrics_in_code)}"
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
