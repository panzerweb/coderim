"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    a, b = int(next(data)), int(next(data))
    output.write(str(a + b) + '\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
