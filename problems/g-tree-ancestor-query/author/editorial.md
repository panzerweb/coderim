# Private organizer notes: G-Tree Node Ancestor Query

An iterative DFS assigns entry times and exclusive exit times. U is an ancestor of V exactly when tin[U] <= tin[V] < tout[U]. Use an explicit stack so a chain of 100,000 nodes does not overflow the call stack.

Time: {'Preprocessing': 'O(N)', 'Each query': 'O(1)', 'Total': 'O(N + Q)'}. Auxiliary space: O(N).

Alternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.

Regenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.
