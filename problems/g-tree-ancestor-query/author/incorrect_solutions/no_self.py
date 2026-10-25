"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    n = int(next(data))
    children = [[] for _ in range(n + 1)]
    for _ in range(n - 1):
        p, c = int(next(data)), int(next(data))
        children[p].append(c)
    tin, tout = [0] * (n + 1), [0] * (n + 1)
    stack, clock = [1], 0
    while stack:
        node = stack.pop()
        if node < 0:
            tout[-node] = clock
        else:
            tin[node] = clock
            clock += 1
            stack.append(-node)
            stack.extend(children[node])
    for _ in range(int(next(data))):
        u, v = int(next(data)), int(next(data))
        output.write('YES\n' if tin[u] < tin[v] < tout[u] else 'NO\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
