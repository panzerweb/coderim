import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.problems import Repository

if __name__ == '__main__':
    repo = Repository(ROOT / 'problems')
    for key, error in repo.errors.items():
        print(f'INVALID {key}: {error}')
    for p in repo.problems.values():
        print(f'OK {p.meta.id} v{p.meta.version}: {len(p.cases)} cases, {p.meta.status}')
    sys.exit(1 if repo.errors or not repo.problems else 0)
