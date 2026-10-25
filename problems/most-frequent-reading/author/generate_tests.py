from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from practice_problem_content import generate
if __name__=='__main__':
    generate(Path(__file__).resolve().parents[1].name)
