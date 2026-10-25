"""Private organizer reference; auxiliary bounds exclude stored I/O."""
import sys

def tokens(stream):
    for line in stream:
        yield from line.split()

def solve(stream, output):
    data = iter(tokens(stream))
    from collections import deque
    rows, cols = int(next(data)), int(next(data))
    grid = [next(data) for _ in range(rows)]
    start = next((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 'S')
    distance = [[-1] * cols for _ in range(rows)]
    distance[start[0]][start[1]] = 0
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if grid[r][c] == 'E':
            output.write(str(distance[r][c]) + '\n')
            return
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != '#' and distance[nr][nc] < 0:
                distance[nr][nc] = distance[r][c] + 1
                queue.append((nr, nc))
    output.write('-1\n')

if __name__ == '__main__':
    solve(sys.stdin, sys.stdout)
