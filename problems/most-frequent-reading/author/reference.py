"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    counts = {}
    for _ in range(int(next(data))):
        value = int(next(data))
        counts[value] = counts.get(value, 0) + 1
    value = min(counts, key=lambda x: (-counts[x], x))
    output.write(f'{value} {counts[value]}\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
