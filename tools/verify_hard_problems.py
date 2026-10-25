"""Authoring-only language verification and limit calibration, not runtime inference."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
import app.judge as judge_module
from app.judge import Judge
from app.languages import Registry
from app.problems import load_problem

FILES = {'python': 'reference.py', 'javascript': 'reference.js', 'cpp': 'reference.cpp', 'java': 'Main.java'}


def main(slugs=None, report_name='results.json'):
    registry = Registry()
    runtime = ROOT / '.runtime/content-verification'
    runtime.mkdir(parents=True, exist_ok=True)
    records = []
    for slug in slugs or ('longest-rising-streak-updates', 'g-tree-changing-root'):
        directory = ROOT / 'problems' / slug
        p = load_problem(directory)
        for language, filename in FILES.items():
            if not registry.status[language]['available']:
                print(f'SKIP {language}: {registry.status[language]["reason"]}', flush=True)
                continue
            durations = []
            real_execute = judge_module.execute
            def measured(*args, **kwargs):
                result = real_execute(*args, **kwargs)
                durations.append(result.duration_ms)
                return result
            with tempfile.TemporaryDirectory(dir=runtime) as temp:
                judge = Judge(registry, Path(temp))
                with patch.object(judge_module, 'execute', measured):
                    result = judge.run(p, language, (directory / 'author' / filename).read_text(encoding='utf-8'))
                if result['verdict'] != 'Accepted':
                    raise AssertionError(f'{slug}/{language} failed: {result}')
                starter = judge.run(p, language, p.starters[language], mode='samples')
                if starter['verdict'] in ('Compile Error', 'Runtime Error', 'Judge Error', 'Time Limit Exceeded'):
                    raise AssertionError(f'{slug}/{language} starter does not parse samples: {starter}')
            maximum = max(durations[1:])
            record = {'problem': slug, 'language': language, 'cases': result['total'],
                'verdict': result['verdict'], 'max_case_ms': maximum, 'limit_ms': p.meta.limits.time_ms,
                'case_durations_ms': dict(zip((c.id for c in p.cases), durations[1:]))}
            records.append(record)
            print(f'{slug}/{language}: {result["passed"]}/{result["total"]}, max case {maximum:.2f} ms / {p.meta.limits.time_ms} ms', flush=True)
    (runtime / report_name).write_text(json.dumps(records, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
