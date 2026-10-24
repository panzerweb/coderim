import sys

data = (token for line in sys.stdin.buffer for token in line.split())
n = int(next(data))
edges = [(int(next(data)), int(next(data))) for _ in range(n - 1)]
# TODO: prepare your data structure for the tree initially rooted at 1.
q = int(next(data))
for _ in range(q):
    command = next(data).decode()
    if command == 'ROOT':
        root = int(next(data))
        # TODO: change the logical root.
    else:
        u, v = int(next(data)), int(next(data))
        # TODO: print YES or NO for QUERY u v.
