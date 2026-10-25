# Private organizer reference: Next Permutation

Find the rightmost position whose value is smaller than its successor. Swap it with the rightmost larger value, then reverse the suffix. If no pivot exists, reverse the whole array. Use explicit swaps/two pointers rather than allocating a suffix copy in references. Tests observe mutation through the supplied driver; space compliance remains a manual review dimension.

Time: {'Find pivot, swap, and reverse': 'O(N)'}. Auxiliary space: O(1) auxiliary space, excluding stored input and serialized output. Account separately for retained input and serialized results.

Regenerate using author/generate_tests.py. Outputs use independent arbitrary-precision, sorted-set, multiset-ranking, or small-substring oracles. Large string patterns have independently known answers. Tests observe outputs; they do not enforce internal allocation behavior.
