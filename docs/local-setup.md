# Local operation

Run `scripts/setup.ps1` once with internet to create `.venv`, install pinned Python dependencies, install the npm lockfile, build Monaco and application assets, and validate content. Run `scripts/start.ps1` to serve both the built SPA and API at http://127.0.0.1:8000. Deep links such as `/problems/broken-code-formatter` work through the SPA fallback.

For development, the frontend runs on port 5173 and proxies `/api` to 8000. Both frontend and backend bind to loopback. The API accepts local hosts, validates browser origins on JSON mutations, and bounds request bodies. Browser assets, fonts, editor workers, statements, and data are served locally, so normal operation does not need network access.

Optional operator environment settings: `RELAY_PROBLEMS` (problem root), `RELAY_RUNTIME` (runtime root), `RELAY_FRONTEND_ORIGIN` (an additional explicitly allowed frontend origin), and executable paths documented in `adding-languages.md`. Do not expose the server to untrusted participants; an isolated executor must be added before shared event hosting.

SQLite schema version 2 bootstraps automatically. Version 1 migrates transactionally by adding a nullable reference-complexity context column; existing sources, results, rubrics, ratings, and explanations are preserved. Failed migrations roll back and close the connection. Unknown database versions fail startup rather than overwriting history. Stop the backend before backing up the runtime directory (including any SQLite WAL files). Drafts are stored separately by the browser. Clearing browser storage removes drafts; deleting the runtime database removes durable attempts and reviews.

Execution uses unique build/case directories, fixed argument arrays, no shell execution, a minimal environment, concurrent bounded stdout/stderr readers, and whole-tree termination. Compiled/source artifacts are marked read-only before reuse. Windows uses kill-on-close Job Objects; Unix uses process groups. Files are cleaned on completion, failure, timeout, and active-job shutdown. These mechanisms constrain ordinary trusted programs and do not prevent malicious filesystem access or provide an isolation boundary.

Shutting down cancels active work. Queued or unfinished persisted attempts are marked interrupted on the next startup; completed source/results/reviews survive. Source/rubric/result snapshots are immutable through the API; human reviews are editable. Runs only exist in the expiring job registry.

Problem DTOs and attempt DTOs expose optional `reference_complexity`; attempts use the frozen value. Review updates accept optional `complexity` with status `assessed` or `unable_to_assess`, `worst_case_time`, `auxiliary_space`, `total_space`, and `reasoning`. Assessed reviews require all bounds; unable-to-assess reviews require a reason and null bounds. Omitted/null complexity preserves prior reviewed analysis for older clients. There is no automatic complexity analyzer or peak-memory metric.
