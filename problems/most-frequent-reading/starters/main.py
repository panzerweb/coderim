import sys

data = (word for line in sys.stdin for word in line.split())
n = int(next(data))
values = [int(next(data)) for _ in range(n)]
# TODO: print the most frequent value and its frequency; smallest value wins ties.
