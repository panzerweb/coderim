# Private organizer notes: Palindrome Check

Use pointers from both ends. Skip non-alphanumeric characters and compare remaining characters after case folding. The pointers use constant extra space; storing or normalizing the whole line consumes O(L) total space.

Time: {'Two-pointer comparison': 'O(L)'}. Auxiliary space: O(1) beyond the stored input line.

Alternative correct algorithms are allowed. Expected hash-map time is not a worst-case guarantee. Account for materialized input, output, and stacks separately. Tests assess observable behavior.

Regenerate with `python author/generate_tests.py`; use the repository verification tool before publishing. Sample outputs are fixed explicitly; small hidden outputs use an independent oracle. Scale outputs use known patterns or a separate linear oracle.
