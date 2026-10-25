"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    for _ in range(int(next(data))):
        n = int(next(data))
        previous = int(next(data))
        best = current = 1
        for _ in range(n - 1):
            value = int(next(data))
            current = current + 1 if value > previous else 1
            best = max(best, current)
            previous = value
        output.write(str(best) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
