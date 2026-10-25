# Private organizer reference: Remove Duplicates from Sorted Array

Keep a write index k. Scan left to right and write a value only when it differs from the last written value, then increment k. The driver checks k and the mutated prefix, not the tail. A new local binding does not update the caller. Constant-space compliance is reviewed from source under Technical Quality; output tests do not prove allocation behavior.

Time: {'Compaction': 'O(N)'}. Auxiliary space: O(1) auxiliary space; the provided driver stores/serializes O(K) result data. Account separately for retained input and serialized results.

Regenerate using author/generate_tests.py. Outputs use independent arbitrary-precision, sorted-set, multiset-ranking, or small-substring oracles. Large string patterns have independently known answers. Tests observe outputs; they do not enforce internal allocation behavior.
