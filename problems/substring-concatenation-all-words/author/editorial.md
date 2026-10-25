# Private organizer reference: Substring with Concatenation of All Words

Count required words, then scan K aligned windows. Reset when an unknown word occurs; shrink from the left when the new word is overrepresented. Record a start when the window contains M words, then advance one word so overlaps remain possible. Do not sort the result: output order is unrestricted. Hashing and substring creation contribute a K factor. Hash-table operation bounds are expected, not worst-case guarantees.

Time: {'Build word counts': 'Expected O(MK)', 'Scan all offsets': 'Expected O(NK)', 'Return indices': 'O(A)'}. Auxiliary space: O(DK) working space, excluding input and O(A) returned output. Include input/output storage and serialization when reviewing total space. The reference is not a required implementation.

Generate with `python author/generate_tests.py`; verify with the repository's function-problem verification tool. Saved samples have explicitly checked expected results. Random small cases use independent oracles; substring scale cases use known patterns.
