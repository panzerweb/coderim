# Hosted revision verification

Verified on Windows with Python 3.12 and the installed Node/Java toolchains:

- 62 backend tests: original content/comparator/scoring/complexity and process-control regressions, schema 1/2 migration preservation, authentication/CSRF/CORS, ownership, five-team queue load, five-versus-four solved fixtures, manual start, real provider-free execution, local startup/bootstrap, and optional managed recovery.
- Four original practice browser scenarios, covering all three challenges, reviews, old attempts, drafts, responsive editing, and unavailable backend behavior.
- One full contest browser scenario using separate organizer/team contexts and real local Python execution: publication/waiting, manual start, all three challenges, confirmation cancellation, lost-response retry after editing, private history, session reset/rejoin, draft isolation/recovery, organizer per-team history/source inspection and complexity review, and ended read-only access.
- Nine formatter example programs: Python/JavaScript/Java each still pass exactly 1, 3, or all 65 official cases (and 1, 3, or 6 visible samples).
- Both hard-challenge reference suites pass in Python, JavaScript, and Java within the provisional five-second per-case limits. Local C++ checks were skipped because `g++` is not installed; managed C++ remains subject to live provider verification.
- Frontend TypeScript check and production build; production smoke covers all three challenges, deep-link reloads, real Monaco edits/workers, and local asset delivery.

Managed-provider tests use deterministic fakes and HTTP mock transports; they consume no paid executions and explicitly forbid local subprocesses during managed judging. Provider-free contest tests use the original real executor and forbid constructing Judge0 clients. Screenshots are generated under the ignored `.runtime/` QA directory. Test databases and five extra problem fixtures are temporary; the production catalog still has three challenges.

Actual Render deployment, custom-domain cookies/CORS, and sustained hosted capacity require staging verification. The Docker CLI is installed but its Linux engine was stopped; the new image could not be built/run here. No live deployment is claimed. Provider-free publication/execution has no provider checks. If managed execution is explicitly selected, its separate opt-in compatibility checks still apply. See [the operator guide](hosted-contests.md).
