# Shortest Grid Route

Find the fewest moves from S to E in a grid. Each move goes one cell up, down, left, or right. You cannot leave the grid or enter a wall (#). Every move costs one.

## Input specification

Read R C (1 <= R,C <= 500; R*C >= 2), followed by R rows of exactly C symbols. A dot (.) is open, # is a wall, S is the unique start, and E is the unique exit. Start and exit occupy distinct cells.

## Output specification

Print the minimum number of moves from S to E, or -1 if no route exists. Count moves, not visited cells.

## Practice information

Suggested duration: 40 minutes (informational). Execution target: 2 seconds per case. Memory target: 256 MB, unenforced by the local executor.
