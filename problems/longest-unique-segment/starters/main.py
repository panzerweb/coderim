import sys

data = (word for line in sys.stdin for word in line.split())
n = int(next(data))
values = [int(next(data)) for _ in range(n)]
# TODO: print the longest consecutive segment with distinct values.
