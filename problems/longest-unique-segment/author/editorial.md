# Private organizer notes: Longest Unique Segment

Track the last position of each value. On a repetition, set left = max(left, last[value] + 1), then update the best window length. Never move left backward because of an occurrence outside the current window.

Time: {'Sliding window': 'Expected O(N) with a hash table'}. Auxiliary space: O(D).

Alternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.

Regenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.
