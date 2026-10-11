import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.problems import load_problem, safe_path
from app.judge import normalize


def verify(slug):
    directory = (ROOT / 'problems' / slug).resolve()
    if not directory.is_relative_to((ROOT / 'problems').resolve()):
        raise ValueError('Unsafe slug')
    p = load_problem(directory)
    reference = safe_path(directory, 'author/reference.py')
    for case in p.cases:
        run = subprocess.run([sys.executable, '-I', str(reference)], input=case.stdin,
            capture_output=True, text=True, timeout=5)
        if run.returncode or normalize(run.stdout, p.meta.checker) != normalize(case.expected, p.meta.checker):
            raise ValueError(f'Reference disagrees with {case.id}')
    for incorrect in (directory / 'author' / 'incorrect_solutions').glob('*.py'):
        detected = False
        for case in p.cases:
            run = subprocess.run([sys.executable, '-I', str(incorrect)], input=case.stdin,
                capture_output=True, text=True, timeout=5)
            if run.returncode or normalize(run.stdout, p.meta.checker) != normalize(case.expected, p.meta.checker):
                detected = True
                break
        if not detected:
            raise ValueError(f'Tests did not detect {incorrect.name}')
        print(f'Detected {incorrect.name}')
    print(f'Verified {p.meta.id}: {len(p.cases)} reference outputs')


if __name__ == '__main__':
    try:
        verify(sys.argv[1])
    except (IndexError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        print(f'Verification failed: {error}')
        sys.exit(1)
