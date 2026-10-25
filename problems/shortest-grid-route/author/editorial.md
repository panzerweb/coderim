# Private organizer notes: Shortest Grid Route

Breadth-first search processes cells in increasing distance. Mark a cell when enqueuing it and store its distance, starting at 0 for S. DFS finding an arbitrary path does not guarantee the shortest route.

Time: {'Breadth-first search': 'O(RC)'}. Auxiliary space: O(RC).

Alternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.

Regenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.
