# Private organizer notes: Longest Rising Streak

Keep the previous temperature, the current rising run length, and the best length. Reset the current length to 1 at every non-increase. Reset all state between cases.

Time: {'All cases': 'O(sum N)'}. Auxiliary space: O(1) when processing temperatures sequentially.

Alternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.

Regenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.
