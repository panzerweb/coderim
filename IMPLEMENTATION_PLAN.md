# Code Relay Judge — reconciled implementation specification

This implementation preserves the architecture of `code_relay_judge_implementation_plan.md` and incorporates the approved assessment/progress changes. The original document's in-memory-only history, stop-at-first-failure rule, and no-database default are superseded here.

## User flow

Homepage → Start → dynamic problem library → statement/Monaco workspace → samples or custom-input exploration → official submission → criteria/evidence → local human review → progress across attempts.

## Assessment

Functional Correctness 50%, Requirement Completion 20%, Readability/Maintainability 15%, Organization/Technical Quality 15%. Automated correctness uses category pass rates; requirements use all-mapped-tests-passed evidence. Human criteria each have four 0–4 dimensions and a required rationale. Final scores remain pending until review. Acceptance requires all official tests, independently of rubric points.

The Broken Code Formatter uses the supplied six samples and category weights (15/20/20/20/15/10), plus a verified hidden suite. Four equally weighted requirement conditions match the participant statement. Official judging continues after failures, but preserves the first failure's verdict. Infrastructure/budget failure leaves assessment incomplete. Compilation failure gives zero automated scores.

## Contracts and persistence

The versioned file-based package includes safe relative paths, authoritative samples, saved hidden input/output files, category mappings, requirement mappings, duration, resource targets, and rubric definitions. API routes expose published problems, toolchain availability, runs, submissions, jobs, attempt history, source snapshots, and review updates. Hidden-case data and author materials never appear in participant DTOs.

SQLite stores source/result/rubric snapshots and reviews. Job execution remains a bounded in-memory single-worker queue. Restart interrupts unfinished attempts, while completed history survives. Drafts and progress comparisons are separated by problem/version/language.

## Boundaries and verification

Trusted local practice only; no accounts, AI, leaderboard, cloud, enforced practice timer, or participant handoffs. All assets run offline after setup. Memory enforcement and Docker isolation remain deferred.

Verification covers content/oracle agreement, invalid packages, comparator behavior, judge verdicts, process-tree termination, budget failures, scores, persistence, origins/privacy, responsive APIs, queue overload/expiry, frontend flow/drafts/reviews, and a temporary second-problem extension. See README for executable verification commands.
