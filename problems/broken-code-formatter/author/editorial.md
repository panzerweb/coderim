# Organizer notes

Use a bracket stack, an active quote (none, single, or double), and an escape flag. Visit each character once. Inside a string, process escape state before interpreting backslashes or the matching quote. Outside strings, push opening brackets and match closing brackets against the stack top. Accept only with an empty stack, no active quote, and no dangling escape.

Time is O(L); worst-case space is O(L). Equivalent correct algorithms are allowed. No participant code is inspected for a mandatory stack implementation.

Run `python problems/broken-code-formatter/author/generate_tests.py` to rebuild saved cases, then `python tools/verify_problem.py broken-code-formatter`. The generator uses seed 3003. The test suite includes transport-independent spaces, opposite quotes, odd/even backslashes, literal outside-string backslashes, comments/backticks without special handling, and length-100000 cases.

The verifier checks fixed expected outputs, samples, and intentionally faulty solutions. Backend tests additionally compare the reference against an independent tokenization-and-reduction oracle on small inputs.
