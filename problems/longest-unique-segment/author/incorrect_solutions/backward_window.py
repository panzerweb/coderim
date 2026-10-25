"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    last = {}
    left = best = 0
    for right in range(int(next(data))):
        value = int(next(data))
        left = last.get(value, -1) + 1
        last[value] = right
        best = max(best, right - left + 1)
    output.write(str(best) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
