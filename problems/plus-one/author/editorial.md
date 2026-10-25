# Private organizer reference: Plus One

Visit digits from right to left. Increment the first digit below nine and stop; replace each carried-through nine by zero. If all digits were nine, return a leading one followed by the zeros. Input mutation is allowed, not required. Never rely on fixed-width or floating-point numeric conversion.

Time: {'Worst-case carry propagation': 'O(N)'}. Auxiliary space: O(1) working space, excluding returned output of up to N+1 digits. Account separately for retained input and serialized results.

Regenerate using author/generate_tests.py. Outputs use independent arbitrary-precision, sorted-set, multiset-ranking, or small-substring oracles. Large string patterns have independently known answers. Tests observe outputs; they do not enforce internal allocation behavior.
