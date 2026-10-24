import sys
data = iter(sys.stdin.read().split())
n = int(next(data)); parent = [1] * (n + 1)
for _ in range(n - 1):
    p, c = int(next(data)), int(next(data)); parent[c] = p
for _ in range(int(next(data))):
    if next(data) == 'ROOT':
        next(data)
    else:
        u, v = int(next(data)), int(next(data))
        while v != 1 and v != u:
            v = parent[v]
        print('YES' if v == u else 'NO')
