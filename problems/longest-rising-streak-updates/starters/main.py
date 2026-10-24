import sys

data = (token for line in sys.stdin.buffer for token in line.split())
test_cases = int(next(data))
for _ in range(test_cases):
    n, q = int(next(data)), int(next(data))
    temperatures = [int(next(data)) for _ in range(n)]
    # TODO: prepare your data structure for this test case.
    for _ in range(q):
        command = next(data).decode()
        a, b = int(next(data)), int(next(data))
        # TODO: UPDATE a b, or print the answer for QUERY a b.
