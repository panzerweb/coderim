"""Organizer reference: ordered segment summaries, streaming operations/output."""
import sys


def merge(a, b):
    if a is None:
        return b
    if b is None:
        return a
    an, af, al, ap, az, ab = a
    bn, bf, bl, bp, bz, bb = b
    joins = al < bf
    prefix = an + bp if joins and ap == an else ap
    suffix = bn + az if joins and bz == bn else bz
    return (an + bn, af, bl, prefix, suffix, max(ab, bb, az + bp if joins else 0))


class SegmentTree:
    def __init__(self, values):
        self.size = 1 << (len(values) - 1).bit_length()
        self.tree = [None] * (2 * self.size)
        for i, x in enumerate(values):
            self.tree[self.size + i] = (1, x, x, 1, 1, 1)
        for i in range(self.size - 1, 0, -1):
            self.tree[i] = merge(self.tree[i * 2], self.tree[i * 2 + 1])

    def update(self, index, value):
        i = self.size + index
        self.tree[i] = (1, value, value, 1, 1, 1)
        i //= 2
        while i:
            self.tree[i] = merge(self.tree[i * 2], self.tree[i * 2 + 1])
            i //= 2

    def query(self, left, right):
        left += self.size
        right += self.size + 1
        before = after = None
        while left < right:
            if left & 1:
                before = merge(before, self.tree[left])
                left += 1
            if right & 1:
                right -= 1
                after = merge(self.tree[right], after)
            left //= 2
            right //= 2
        return merge(before, after)[5]


def tokens(stream):
    for line in stream:
        yield from line.split()


def solve(stream, output):
    data = iter(tokens(stream))
    for _ in range(int(next(data))):
        n, q = int(next(data)), int(next(data))
        tree = SegmentTree([int(next(data)) for _ in range(n)])
        for _ in range(q):
            command, a, b = next(data), int(next(data)), int(next(data))
            if command == 'UPDATE':
                tree.update(a - 1, b)
            else:
                output.write(str(tree.query(a - 1, b - 1)) + '\n')


if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
