"""Organizer reference: iterative Euler tour and binary lifting."""
import sys


class AncestorTree:
    def __init__(self, n, edges):
        adjacent = [[] for _ in range(n)]
        for p, c in edges:
            adjacent[p].append(c)
            adjacent[c].append(p)
        self.depth = [0] * n
        self.tin, self.tout = [0] * n, [0] * n
        parent = [0] * n
        clock = 0
        stack = [(0, -1, False)]
        while stack:
            node, previous, exiting = stack.pop()
            if exiting:
                self.tout[node] = clock
                continue
            parent[node] = node if previous < 0 else previous
            self.tin[node] = clock
            clock += 1
            stack.append((node, previous, True))
            for child in adjacent[node]:
                if child != previous:
                    self.depth[child] = self.depth[node] + 1
                    stack.append((child, node, False))
        self.up = [parent]
        for _ in range(1, n.bit_length()):
            previous = self.up[-1]
            self.up.append([previous[previous[v]] for v in range(n)])

    def fixed_ancestor(self, u, v):
        return self.tin[u] <= self.tin[v] < self.tout[u]

    def ancestor(self, root, u, v):
        if u == v or u == root:
            return True
        if not self.fixed_ancestor(u, root):
            return self.fixed_ancestor(u, v)
        distance = self.depth[root] - self.depth[u] - 1
        child, bit = root, 0
        while distance:
            if distance & 1:
                child = self.up[bit][child]
            distance >>= 1
            bit += 1
        return not self.fixed_ancestor(child, v)


def tokens(stream):
    for line in stream:
        yield from line.split()


def solve(stream, output):
    data = iter(tokens(stream))
    n = int(next(data))
    edges = [(int(next(data)) - 1, int(next(data)) - 1) for _ in range(n - 1)]
    tree = AncestorTree(n, edges)
    root = 0
    for _ in range(int(next(data))):
        command = next(data)
        if command == 'ROOT':
            root = int(next(data)) - 1
        else:
            u, v = int(next(data)) - 1, int(next(data)) - 1
            output.write('YES\n' if tree.ancestor(root, u, v) else 'NO\n')


if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
