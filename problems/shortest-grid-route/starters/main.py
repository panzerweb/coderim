import sys

data = (word for line in sys.stdin for word in line.split())
rows, cols = int(next(data)), int(next(data))
grid = [next(data) for _ in range(rows)]
# TODO: print the shortest four-direction route length, or -1.
