# Code Relay Judge — reconciled implementation specification

This implementation preserves the architecture of `code_relay_judge_implementation_plan.md` and incorporates the approved assessment/progress changes. The original document's in-memory-only history, stop-at-first-failure rule, and no-database default are superseded here.

## User flow

Homepage → Start → dynamic problem library → statement/Monaco workspace → samples or custom-input exploration → official submission → criteria/evidence → local human review with optional complexity reasoning → progress across attempts.

## Assessment

Functional Correctness 50%, Requirement Completion 20%, Readability/Maintainability 15%, Organization/Technical Quality 15%. Automated correctness uses category pass rates; requirements use all-mapped-tests-passed evidence. Human criteria each have four 0–4 dimensions and a required rationale. Final scores remain pending until review. Acceptance requires all official tests, independently of rubric points.

The Broken Code Formatter uses the supplied six samples and category weights (15/20/20/20/15/10), plus a verified hidden suite. Four equally weighted requirement conditions match the participant statement. Official judging continues after failures, but preserves the first failure's verdict. Infrastructure/budget failure leaves assessment incomplete. Compilation failure gives zero automated scores.

## Contracts and persistence

The versioned file-based package includes safe relative paths, authoritative samples, saved hidden input/output files, category mappings, requirement mappings, duration, resource targets, and rubric definitions. API routes expose published problems, toolchain availability, runs, submissions, jobs, attempt history, source snapshots, and review updates. Hidden-case data and author materials never appear in participant DTOs.

SQLite stores source/result/rubric snapshots and reviews. Job execution remains a bounded in-memory single-worker queue. Restart interrupts unfinished attempts, while completed history survives. Drafts and progress comparisons are separated by problem/version/language.

Schema 2 adds nullable frozen reference-complexity context, with a transactional version-1 migration. Review annotations cover worst-case time, auxiliary space, total space including stored input/output, and reasoning, or an explicit inability to assess. These are reviewer-only fields; reference targets, human assessments, and measured runtime remain separate. Missing legacy data is not backfilled from current content. Existing review clients preserve saved complexity when omitting it. Scoring and acceptance remain unchanged.

## Additional Hard challenges

Longest Rising Streak with Updates supports UPDATE I X and QUERY L R across independent test cases. Its ordered segment-tree reference has O(N) build, O(log N) operations, and O(N) auxiliary space. G-Tree: Ancestors with a Changing Root supports ROOT R and QUERY U V on fixed edges; its iterative traversal/binary-lifting reference has O(N log N) preprocessing/space, O(1) root changes, and O(log N) queries. Both are provisional Hard/60-minute challenges for DSA students, pending representative human pilots.

Their versioned packages include verified samples, hidden tests, independent small-case oracles, deterministic generators, faulty solutions, fast input starters in four languages, and private reference implementations. Streak category weights are 15/15/20/25/10/15; tree category weights are 15/15/25/20/10/15. Each has four equally weighted behavioral requirements. Inputs may require the new 8 MiB operator ceiling and output up to 2 MiB; original package limits, 100-case/20 MiB package bounds, and the formatter's 65 cases are preserved.

## Boundaries and verification

Trusted local practice only; no accounts, AI, leaderboard, cloud, enforced practice timer, or participant handoffs. All assets run offline after setup. Memory enforcement and Docker isolation remain deferred.

Verification covers content/oracle agreement, invalid packages, comparator behavior, judge verdicts, process-tree termination, budget failures, scores, persistence, origins/privacy, responsive APIs, queue overload/expiry, frontend flow/drafts/reviews, and a temporary second-problem extension. See README for executable verification commands.
