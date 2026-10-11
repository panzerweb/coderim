# Code Relay Judge

A local coding workspace: **Home → Problem library → Code and test → Submit → Review and progress**.

Vue, TypeScript, Monaco, FastAPI, file-based challenges, and SQLite history. No account, AI key, or cloud service. The first challenge is **The Broken Code Formatter** (Hard): six samples and 59 hidden cases.

## Windows quick start

Install Python 3.12+ and Node.js 22.12+. From this project folder in PowerShell:

```powershell
.\scripts\setup.ps1
.\scripts\start.ps1
```

Open **http://127.0.0.1:8000**. Setup installs dependencies and builds all frontend assets locally; subsequent starts require no internet. If PowerShell script execution is restricted, use `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1` for this script invocation.

Programs run with the operating-system permissions of this computer's user. Use trusted code. Local process limits are not a security sandbox. Hidden tests are hidden in the UI but inspectable on disk. The 256 MB memory target is unenforced. Shared event hosting and isolated execution are outside this release.

## Development and verification

```powershell
.\scripts\setup.ps1 -Dev
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.\.venv\Scripts\python.exe tools/verify_problem.py broken-code-formatter
```

For frontend development, run the backend as above and run `npm run dev` inside `frontend/`. Open http://127.0.0.1:5173. The Vite server proxies `/api` to the backend.

```powershell
cd frontend
npm run build
npx playwright install chromium
npm run test:e2e
```

Browser tests manage an isolated backend and frontend on ports 8000/5173; stop existing servers on those ports before running. They use `.runtime/e2e/`, separate from normal history. Chromium is only required for tests.

With the built application running at port 8000, `npm run test:production` inside `frontend/` checks deep links, real Monaco editing, local worker assets, and the absence of external runtime requests. It does not submit attempts or alter your browser's drafts.

For macOS/Linux: create `.venv` with `python3 -m venv .venv`, install `backend/requirements.txt`, run `npm ci && npm run build` inside `frontend`, then run `sh scripts/start.sh`. Windows is the verified primary platform.

## Scoring and history

Functional Correctness (50%) and Requirement Completion (20%) are calculated from the official suite. Readability (15%) and Technical Quality (15%) are reviewed manually on each saved source snapshot. Missing reviews remain pending. **Accepted always means every official test passed**; rubric points cannot override the verdict.

Drafts live in browser storage, keyed by problem/version/language. Official submissions, frozen rubrics, judge results, and reviews live in `.runtime/history.sqlite3`. Restarting the backend interrupts unfinished jobs but preserves completed attempts. The timeline shows the latest 200 attempts for the current version/language. Runs are transient and never contribute to official scores.

See [judging rules](docs/judging-rules.md), [adding problems](docs/adding-problems.md), [language setup](docs/adding-languages.md), and [local setup](docs/local-setup.md). The reconciled implementation specification is [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md); the original blueprint remains for reference.
