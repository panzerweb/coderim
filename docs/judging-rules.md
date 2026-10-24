# Judging and assessment

Run samples to compare visible expected outputs, or run custom input to inspect stdout/stderr and exit status. Custom input never produces a correctness score. Submit compiles once and runs samples plus all hidden cases in deterministic manifest order, each in a fresh process and working directory.

The first failing case determines the verdict, while subsequent cases still run to calculate assessment coverage. Verdicts: Accepted, Wrong Answer, Compile Error, Runtime Error, Time Limit Exceeded, Output Limit Exceeded, and Judge Error. A successful custom run is Completed. Compiler diagnostics are capped independently. Per-case stdout/stderr caps and a separate compiler timeout are enforced; there is no Memory Limit Exceeded claim.

Text comparison normalizes CRLF/lone CR to LF, removes trailing spaces/tabs per line, and ignores one final newline when configured. Leading spaces, internal spaces, letter case, extra blank lines, debug text, and prompts remain significant.

Each category earns `weight × passed / total`. The first problem uses basic 15, nesting 20, quotes 20, escapes 20, unclosed 15, and large 10. Each test belongs to one category, including samples. A requirement earns equal credit only if all mapped tests pass. Mappings may overlap; correctness and requirements measure related behavior rather than independent properties. Required coverage is validated before publication.

Each human criterion has four dimensions, scored 0–4 (missing, weak, partial, good, strong). Its score is `mean(ratings) × 25`. A rationale is required. The total is `0.50C + 0.20R + 0.15M + 0.15T`, rounded to two decimals, and appears only after a complete automated assessment plus human review. Reviewers judge the saved source, not the current editor draft. Review edits update the reviewed score without changing the source, original test results, or frozen rubric.

Compile Error gives zero automated scores. Infrastructure failure, restart interruption, or overall budget exhaustion leaves scores incomplete (null), not zero. Final scores do not change acceptance. Runtime is diagnostic and includes local startup overhead; total job time includes compilation and all tests. The interface does not infer complexity or compare runtime percentiles across machines/languages.

## Human complexity review

The reviewer can record worst-case time, auxiliary space (working structures and recursion), total space including retained input/output, and an explanation tied to the immutable source snapshot. An **Unable to assess** review has an explanation and no asserted bounds. A missing review is **Not assessed**. The application neither parses these annotations as proofs nor assigns them automatic efficiency points.

Reference targets contain problem variables, time by phase/operation, auxiliary space, and explanatory notes. New attempts freeze these targets at submission. Changing problem metadata does not change old analysis or fill missing historical context. The formatter target is O(L) time/O(L) auxiliary space. The streak reference builds in O(N), performs UPDATE/QUERY in O(log N), and uses O(N) auxiliary space per case; total time is O(sum(N + Q log N)). The tree reference preprocesses in O(N log N), changes roots in O(1), answers queries in O(log N), and uses O(N log N) auxiliary space.

Use reviewed reasoning as evidence for the existing Algorithm/data structures and complexity-related Technical Quality dimensions; the 50/20/15/15 weights and manual ratings do not change. Passing test cases does not establish an asymptotic bound. In particular, storing all tokens or answers may increase total program space even when the algorithm's auxiliary bound is small.

Hidden-case inputs, expected outputs, test identifiers, stderr, and captured stdout are excluded from participant results and history. Samples and custom runs expose bounded outputs. Aggregate category and requirement counts are public evidence. Local files and the database are accessible to this computer's user; UI privacy is not secure event judging.

The queue has one worker and ten waiting jobs by default. Completed polling jobs expire after one hour; SQLite submissions remain. Default overall budget is 120 seconds, compilation timeout 15 seconds, and problem per-case limits are bounded to 5 seconds. These operator defaults can be changed through `create_app` / `Judge` configuration, not participant requests.

Operator ceilings are 8 MiB decoded stdin and 2 MiB stdout per case; individual packages retain lower limits where configured. The formatter retains its original 1 MiB input/output limits. The streak package uses 8 MiB/2 MiB; G-Tree uses 8 MiB/1 MiB. Request-body admission allows worst-case JSON escaping, followed by character/schema and decoded UTF-8 byte validation. Suites remain bounded to 100 official inputs and 20 MiB of saved case data per package. An official input may contain multiple logical test cases but still counts as one app case.
