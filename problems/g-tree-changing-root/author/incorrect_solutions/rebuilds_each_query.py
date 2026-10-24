import sys
data = iter(sys.stdin.read().split()); n = int(next(data))
adjacent = [[] for _ in range(n + 1)]
for _ in range(n - 1):
    p, c = int(next(data)), int(next(data)); adjacent[p].append(c); adjacent[c].append(p)
root = 1
for _ in range(int(next(data))):
    if next(data) == 'ROOT':
        root = int(next(data))
    else:
        u, v = int(next(data)), int(next(data))
        parent = [0] * (n + 1); parent[root] = root; todo = [root]
        for node in todo:
            for child in adjacent[node]:
                if not parent[child]:
                    parent[child] = node; todo.append(child)
        while v != u and v != root:
            v = parent[v]
        print('YES' if v == u else 'NO')
