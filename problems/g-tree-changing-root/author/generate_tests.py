import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parents[1] / 'tools'))
from hard_problem_content import generate_tree

if __name__ == '__main__':
    generate_tree(ROOT)
