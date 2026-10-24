import sys
data = iter(sys.stdin.read().split())
for _ in range(int(next(data))):
    n, q = int(next(data)), int(next(data))
    values = [int(next(data)) for _ in range(n)]
    for _ in range(q):
        op, a, b = next(data), int(next(data)), int(next(data))
        if op == 'UPDATE':
            values[a - 1] = b
        else:
            best = current = 1
            for i in range(a, b):
                current = current + 1 if values[i] >= values[i - 1] else 1
                best = max(best, current)
            print(best)
