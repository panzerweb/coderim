import sys

data = (word for line in sys.stdin for word in line.split())
a, b = int(next(data)), int(next(data))
# TODO: print the sum.
