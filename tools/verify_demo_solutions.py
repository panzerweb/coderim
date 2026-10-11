"""Verify diagnostic examples through the real judge without saving attempts."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.judge import Judge
from app.languages import LANGUAGES, Registry
from app.problems import load_problem


def main():
    problem = load_problem(ROOT / 'problems/broken-code-formatter')
    registry = Registry()
    expected = {'pass-1': 1, 'pass-3': 3, 'pass-all': len(problem.cases)}
    summaries = []
    run_root = ROOT / '.runtime' / 'demo-checks'
    run_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=run_root) as temporary:
        judge = Judge(registry, Path(temporary))
        for language in ('python', 'javascript', 'java'):
            if not registry.status[language]['available']:
                raise RuntimeError(f'{language}: {registry.status[language]["reason"]}')
            for variant, count in expected.items():
                path = ROOT / 'examples/judge-checks' / language / variant / LANGUAGES[language].filename
                result = judge.run(problem, language, path.read_text(encoding='utf-8'))
                required_verdict = 'Accepted' if variant == 'pass-all' else 'Wrong Answer'
                if (result['passed'] != count or result['attempted'] != len(problem.cases)
                        or result['verdict'] != required_verdict or not result['assessment']['complete']):
                    raise AssertionError(f'{language}/{variant}: {result}')
                samples_passed = sum(case['verdict'] == 'Accepted' for case in result['cases'])
                if samples_passed != (6 if variant == 'pass-all' else count):
                    raise AssertionError('Unexpected visible sample count')
                entry = {'language': language, 'variant': variant, 'passed': result['passed'],
                    'total': result['total'], 'samples_passed': samples_passed, 'verdict': result['verdict'],
                    'correctness': result['assessment']['correctness'],
                    'requirements': result['assessment']['requirements']}
                summaries.append(entry)
                print(f'{language}/{variant}: {count}/{len(problem.cases)} official, {samples_passed}/6 samples', flush=True)
    (run_root / 'verified-results.json').write_text(json.dumps(summaries, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
