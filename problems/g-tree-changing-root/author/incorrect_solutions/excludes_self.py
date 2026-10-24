import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from reference import AncestorTree
data = iter(sys.stdin.read().split()); n = int(next(data))
tree = AncestorTree(n, [(int(next(data)) - 1, int(next(data)) - 1) for _ in range(n - 1)])
root = 0
for _ in range(int(next(data))):
    if next(data) == 'ROOT':
        root = int(next(data)) - 1
    else:
        u, v = int(next(data)) - 1, int(next(data)) - 1
        print('YES' if u != v and tree.ancestor(root, u, v) else 'NO')
