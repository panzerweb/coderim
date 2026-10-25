# Private organizer reference: Text Justification

Greedily choose the next line using word lengths plus mandatory gaps. For a non-final line with multiple words, divide spare width by the number of gaps and assign the remainder from left to right. Handle final and singleton lines separately. Returned strings occupy O(S) space.

Time: {'Formatting': 'O(C + S)'}. Auxiliary space: O(W) working space, excluding input and returned output. Include input/output storage and serialization when reviewing total space. The reference is not a required implementation.

Generate with `python author/generate_tests.py`; verify with the repository's function-problem verification tool. Saved samples have explicitly checked expected results. Random small cases use independent oracles; substring scale cases use known patterns.
