# Code Relay Judge

A coding workspace with local practice and hosted team contests: **Home → Problem library → Code and test → Record Submission → Review and progress**.

Vue, TypeScript, Monaco, FastAPI, file-based challenges, and SQLite history. Team contests use private sessions and an organizer console around the existing automatic judge. **Judge0 is optional; no provider account is needed for local team contests.** There is no AI integration.

Start with [the team-contest walkthrough](docs/team-contest-quickstart.md). For separate Render deployments, follow [the deployment guide](docs/hosted-contests.md). Actual deployment and custom domains remain organizer tasks.

| Challenge | Official cases | Practice target |
| --- | ---: | --- |
| The Broken Code Formatter | 65 (six samples) | Hard / 60 minutes |
| Longest Rising Streak with Updates | 28 (three samples) | Provisional Hard / 60 minutes |
| G-Tree: Ancestors with a Changing Root | 23 (three samples) | Provisional Hard / 60 minutes |
| Add Two Numbers | 23 (three samples) | Easy / 5 minutes; submission-flow testing |
| Longest Rising Streak | 23 (three samples) | Provisional Easy / 20 minutes |
| Most Frequent Reading | 23 (three samples) | Provisional Easy / 20 minutes |
| Palindrome Check | 23 (three samples) | Provisional Easy / 20 minutes |
| G-Tree Node Ancestor Query | 23 (three samples) | Provisional Medium / 40 minutes |
| Shortest Grid Route | 23 (three samples) | Provisional Medium / 40 minutes |
| Longest Unique Segment | 23 (three samples) | Provisional Medium / 40 minutes |

The catalog contains four Easy, three Medium, and three Hard problems. The Hard variants use point updates/range queries for streaks and logical root changes for tree ancestry. The simpler versions are separate packages. Difficulty and suggested durations are provisional estimates for university DSA students. New introductory packages use a 2-second case limit; the two Hard variants retain their 5-second limits.

Use **Add Two Numbers** for a quick end-to-end check: input `2 3` should output `5`. Run samples, record a submission as a team, then inspect its saved source and add a review as an organizer. Practice runs do not create official history.

After updating, restart the backend to discover new packages. Existing published contests keep their pinned problems; create and publish a new contest to select the additions. No database migration is needed for these content packages. See [introductory problem notes](docs/introductory-problems.md) for contracts and verification commands.

## Deploying with ngrok

This setup runs Code Relay on one hosting computer and exposes it through an HTTPS ngrok URL. No Judge0 account is required.

All teams connect to the same hosting computer through their browsers.

### Prerequisites

Install the following on the hosting computer:

- Git
- Python 3.12 or newer
- Node.js 22.12 or newer
- ngrok, with its authentication token configured

For Java and C++ submissions, also install a JDK and `g++`. Languages with unavailable toolchains are disabled individually.

This uses the existing trusted-code executor. Participant programs run on the hosting computer; it is not a security sandbox.

### 1. Clone and initialize the project

Clone the repository, then open PowerShell inside the cloned project directory.

Run:

```powershell
$env:VITE_API_BASE_URL = ""

powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1

powershell -ExecutionPolicy Bypass -File .\scripts\start-contest.ps1
```

On the first launch, the terminal prompts you to create an organizer username and password.

The launcher also generates and saves the session secret at:

```text
.runtime/session-secret.txt
```

Once the server starts successfully, press **Ctrl+C** to stop it before configuring ngrok.

### 2. Start ngrok

Open a second terminal and run:

```powershell
ngrok http 127.0.0.1:8000
```

Copy the **HTTPS forwarding URL** displayed by ngrok. For example:

```text
https://your-actual-address.ngrok-free.app
```

Keep this terminal running.

### 3. Configure the application for the public URL

Return to the first PowerShell terminal, still inside the project directory.

Replace the example address below with the actual HTTPS URL displayed by ngrok:

```powershell
$relayTunnel = "https://your-actual-address.ngrok-free.app"

$env:RELAY_MODE = "contest"
$env:RELAY_EXECUTOR = "local"
$env:RELAY_DEV_COOKIES = "false"
$env:RELAY_TRUSTED_LOCAL_EXECUTION = "true"
$env:RELAY_FRONTEND_ORIGIN = $relayTunnel
$env:RELAY_ALLOWED_HOSTS = ([uri]$relayTunnel).Host
$env:RELAY_SESSION_SECRET = (Get-Content ".\.runtime\session-secret.txt" -Raw).Trim()

powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1
```

Use **`start.ps1`** for this public startup. The `start-contest.ps1` launcher resets the application settings to localhost.

These environment settings apply to the current PowerShell terminal. Set them again when using a new terminal.

### 4. Access the application

Replace the example hostname with your actual ngrok hostname.

| Page | URL |
|---|---|
| Organizer login | `https://your-actual-address.ngrok-free.app/organizer/login` |
| Organizer console | `https://your-actual-address.ngrok-free.app/organizer` |
| Team join | `https://your-actual-address.ngrok-free.app/join` |

Opening `/organizer` redirects to organizer login when authentication is required.

### 5. Run a contest

1. Sign in through the organizer login page.
2. Create a contest and configure its schedule and duration.
3. Select the problems and publish the contest.
4. Register the teams and privately distribute their generated join codes.
5. Teams open the public `/join` page and enter their team name and code.
6. Wait for the scheduled start or select **Start contest now**.
7. Teams run tests and record their solutions.
8. Organizers inspect each team's submission history, saved source, results, and reviews.

Use separate browser profiles or private windows when testing different teams.

### Subsequent launches

On the same hosting computer:

1. Start ngrok and copy its current HTTPS URL.
2. In PowerShell, open the project directory.
3. Repeat the environment settings from step 3 using that URL.
4. Run `start.ps1`.

Setup and organizer initialization do not need to be repeated for every launch. Run `setup.ps1` again after project updates that require reinstalling dependencies or rebuilding the frontend.

### Important notes

- Keep the hosting computer awake and connected to the internet.
- Keep both the application terminal and ngrok terminal running.
- Teams only need a browser; they do not run separate copies of the application.
- Use the public HTTPS URL consistently for organizer and team access.
- If the ngrok URL changes, update `$relayTunnel` and restart the application with the corresponding environment settings.
- If a team has an active session on an old URL, log out there or use **Reset session** in the organizer console before rejoining.
- Contest data and submission history are stored in `.runtime/history.sqlite3` on the hosting computer.
- Keep the `.runtime` directory private and back up its data using the provided backup tool.
- A fresh clone starts with a fresh database. Existing contests and history require a separate backup transfer.

## Windows quick start

Install Python 3.12+ and Node.js 22.12+. From this project folder in PowerShell:

```powershell
.\scripts\setup.ps1
.\scripts\start.ps1
```

Open **http://127.0.0.1:8000**. Setup installs dependencies and builds all frontend assets locally; subsequent starts require no internet. If PowerShell script execution is restricted, use `powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1` for this script invocation.

For team contests, run `powershell -ExecutionPolicy Bypass -File .\scripts\start-contest.ps1` instead of `start.ps1`. First launch prompts for an organizer account and saves a session secret automatically. Open `/organizer/login`, create/publish the contest, generate team codes, and use the schedule or **Start contest now**. Teams join at `/join`. No provider verification is needed.

The local executor runs programs with its OS user's permissions; use trusted code. Process/time/output limits are not a security sandbox, and the 256 MB memory target is unenforced locally. Hosted trusted-code contests can explicitly choose the same executor through the Docker image. Managed execution is optional and never silently falls back to local processes.

## Development and verification

```powershell
.\scripts\setup.ps1 -Dev
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.\.venv\Scripts\python.exe tools/verify_problem.py broken-code-formatter
.\.venv\Scripts\python.exe tools/verify_problem.py longest-rising-streak-updates
.\.venv\Scripts\python.exe tools/verify_problem.py g-tree-changing-root
.\.venv\Scripts\python.exe tools/verify_hard_problems.py
.\.venv\Scripts\python.exe tools/verify_demo_solutions.py
```

For frontend development, run the backend as above and run `npm run dev` inside `frontend/`. Open http://127.0.0.1:5173. The Vite server proxies `/api` to the backend.

```powershell
cd frontend
npm run build
npx playwright install chromium
npm run test:e2e
npm run test:contest
```

Browser tests manage an isolated backend and frontend on ports 8000/5173; stop existing servers on those ports before running. They use `.runtime/e2e/`, separate from normal history. Chromium is only required for tests.

With the built application running at port 8000, `npm run test:production` inside `frontend/` checks deep links, real Monaco editing, local worker assets, and the absence of external runtime requests. It does not submit attempts or alter your browser's drafts.

For macOS/Linux: create `.venv` with `python3 -m venv .venv`, install `backend/requirements.txt`, run `npm ci && npm run build` inside `frontend`, then run `sh scripts/start.sh`. Windows is the verified primary platform.

## Scoring and history

Functional Correctness (50%) and Requirement Completion (20%) are calculated from the official suite. Readability (15%) and Technical Quality (15%) are reviewed manually on each saved source snapshot. Missing reviews remain pending. **Accepted always means every official test passed**; rubric points cannot override the verdict.

Human reviews can record worst-case time, auxiliary space, total space including stored input/output, and reasoning. Select **Assessed** to enter all three bounds, or **Unable to assess** with an explanation. Reference targets are shown separately and frozen with each new attempt; runtime measurements never become automatic Big-O claims. These annotations support the existing Technical Quality rating without adding a fifth score. Old attempts without saved analysis/context display **Not assessed**.

Drafts live in browser storage, keyed by problem/version/language. Official submissions, frozen rubrics, judge results, and reviews live in `.runtime/history.sqlite3`. Restarting the backend interrupts unfinished jobs but preserves completed attempts. The timeline shows the latest 200 attempts for the current version/language. Runs are transient and never contribute to official scores.

SQLite migrates schemas 1/2 to 3 transactionally on startup, preserving original snapshots, complexity context, and ratings. Contest mode restricts unowned legacy records and review editing to organizers. Existing review clients can omit complexity fields without erasing saved analysis. Local unfinished work becomes interrupted on restart; completed results/reviews survive. Optional managed work resumes saved tokens without blind creation retries.

See [judging rules](docs/judging-rules.md), [adding problems](docs/adding-problems.md), [language setup](docs/adding-languages.md), and [local setup](docs/local-setup.md). The reconciled implementation specification is [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md); the original blueprint remains for reference.

admin12345678
