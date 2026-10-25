import sys

data = (word for line in sys.stdin for word in line.split())
n = int(next(data))
edges = [(int(next(data)), int(next(data))) for _ in range(n - 1)]
# TODO: prepare the fixed-root tree.
for _ in range(int(next(data))):
    u, v = int(next(data)), int(next(data))
    # TODO: print YES or NO for this query.
