import sys

data = (word for line in sys.stdin for word in line.split())
for _ in range(int(next(data))):
    n = int(next(data))
    temperatures = [int(next(data)) for _ in range(n)]
    # TODO: print the longest strictly increasing consecutive streak.
