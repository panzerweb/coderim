# Provider-free contests on Render

The original executor runs tests, calculates correctness, and saves team-owned results in SQLite. **No Judge0 account or verification command is required.** Team authentication and contest management are independent from the executor. Start with [the local walkthrough](team-contest-quickstart.md).

## Execution model

The Dockerfile supplies Python 3.12, Node 22, OpenJDK 17, and C++17. The API and participant programs run under a non-root service user, with time/output limits and process cleanup. This retains the original **trusted-code** execution model: programs share the API's OS user/filesystem, memory is not hard-capped, and the container does not isolate each submission from application data. A public untrusted-code service needs a separate isolated executor; [managed judging](managed-judge.md) is optional.

Public local execution requires the explicit setting `RELAY_TRUSTED_LOCAL_EXECUTION=true`. A failed managed judge never falls back to local execution. Docker packages runtimes; it does not itself provide a per-submission sandbox.

## Backend Web Service

If you only need Python submissions, you can keep a native **Python Web Service** at the repository root: build with `pip install -r backend/requirements.txt` and start with `python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT --workers 1`. Use the same environment/disk settings below. Other languages are available only if their toolchains are installed on that service; the app reports actual availability. This is the simplest provider-free deployment.

For all four toolchains, use the included Docker image instead:

Use the repository root as the Docker build context, keeping `backend/`, `problems/`, `tools/`, and `scripts/` together:

| Render setting | Value |
| --- | --- |
| Language | Docker |
| Dockerfile path | `./Dockerfile` |
| Docker command | Leave empty; use the entrypoint |
| Health check | `/api/health` |
| Instances / workers | One instance / one process |
| Persistent disk mount | `/var/data` |

See [Render Docker deployment](https://render.com/docs/docker). Persistent disks require a paid service; only files beneath their mount survive deploys/restarts. See [Render disks](https://render.com/docs/disks). Keep SQLite and pinned contest files together on that disk.

Set these backend environment variables, replacing the domain and secret values:

```dotenv
RELAY_MODE=contest
RELAY_EXECUTOR=local
RELAY_TRUSTED_LOCAL_EXECUTION=true
RELAY_RUNTIME=/var/data/relay
RELAY_SESSION_SECRET=<persistent random secret of at least 32 characters>
RELAY_FRONTEND_ORIGIN=https://app.example.com
RELAY_ALLOWED_HOSTS=api.example.com
RELAY_DEV_COOKIES=false
```

No `JUDGE0_*` variables are needed. Preserve the session secret across deployments. Optional defaults: `RELAY_TEAM_SESSION_HOURS=4`, `RELAY_ORGANIZER_SESSION_HOURS=8`, `RELAY_QUEUE_CAPACITY=10`, and `RELAY_LOCAL_JOB_SECONDS=120`. The queue has one worker and one active job per team. Existing problem limits/scoring stay unchanged; unavailable languages are disabled individually.

The entrypoint prepares disk ownership and drops root privileges before launching the API. In this image, the runtime path must resolve beneath `/var/data`. Keep a single instance/process because the execution queue is in memory and SQLite resides on one disk.

## Frontend Static Site

| Render setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |
| Environment | `VITE_API_BASE_URL=https://api.example.com` |
| Rewrite | `/*` → `/index.html`, status 200 |

Use HTTPS sibling custom domains, such as `app.example.com` and `api.example.com`, for SameSite=Strict host-only API cookies. Two unrelated `onrender.com` hostnames are not the supported same-site-cookie setup. Configure DNS/TLS through [Render custom domains](https://render.com/docs/custom-domains). Set the exact frontend origin without a path or wildcard. Changing `VITE_API_BASE_URL` requires rebuilding the frontend.

## Organizer setup and event flow

In the deployed backend's Render Shell, run:

```sh
python tools/create_organizer.py --runtime /var/data/relay --username organizer
```

Enter a password of at least 12 characters, then open `https://app.example.com/organizer/login`:

1. Create the contest with an Asia/Manila start and hours/minutes duration (default 3:30).
2. Select problems and publish. This freezes their content and allows waiting teams to join, with no provider gate.
3. Register teams and privately distribute their individual one-time join codes.
4. Let the saved schedule start automatically, or confirm **Start contest now** to begin the full duration immediately.
5. Teams open `/join`, select the contest, and enter their team name/code. Each has private drafts and history.
6. **Run Code** executes samples/custom input. **Record Submission** confirms and saves the exact source, then runs the official suite and saves results/scores. Wrong and incomplete attempts remain recorded.
7. Organizers see all team names, problems, languages, results, and saved sources, with pagination. They enter code-quality/complexity reviews; teams can read their feedback. Distinct Accepted problems and total attempts are separate metrics.
8. After the deadline, new runs/recordings stop while history remains readable. Already admitted work can finish. Organizers can extend an active deadline or explicitly end it early, with confirmation and auditing.

Reset an abandoned team session through the console. Rotate forgotten join codes; their old plaintext cannot be recovered. Rotation and deactivation revoke access immediately.

## Backup and restore

```sh
python tools/contest_backup.py backup /var/data/relay /var/data/relay-backup.zip
python tools/contest_backup.py restore /var/data/relay-backup.zip /var/data/relay-restored
```

Destinations must be new. Backup uses SQLite's backup API and includes pinned content, optional managed state, and the launcher's saved secret when present. Protect backups: they contain private submissions/hidden tests, credential/session hashes, and possibly a session secret. Keep an off-service copy and save Render environment secrets separately.

Stop the backend before switching runtimes. Restore validates database integrity/foreign keys and blocks startup with a marker if incomplete. Local unfinished jobs become interrupted on restart; completed source/results/reviews survive. Managed jobs retain their token recovery behavior. Do not switch executor modes to retry unresolved managed work locally.

Schema-1/2 history migrates transactionally to schema 3. Back up before upgrading; an older application needs its compatible pre-upgrade backup in a new runtime folder.

## Verification before the event

`npm run test:contest` uses separate organizer/team browsers and the real local executor for all three problems. Backend tests run with `.venv/Scripts/python.exe -m unittest discover -s backend/tests -v` on Windows. Rehearse all languages and large cases on the deployed host, verify separate browser sessions, and test backup/restore. Local timings do not establish hosted capacity.

The Docker image must still be built/tested with a running Docker engine or on Render. The engine was unavailable during this implementation; no live deployment is claimed.
