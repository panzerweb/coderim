# Optional managed-judge deployment

This guide applies only when explicitly choosing `RELAY_EXECUTOR=managed`. Judge0 is optional. For the provider-free workflow and Docker deployment, use [the current deployment guide](hosted-contests.md).

Deploy the Vue frontend as a **Static Site**, and FastAPI as a **Web Service**. Use HTTPS sibling domains that you own, such as `app.example.com` and `api.example.com`. SameSite=Strict cookies require this same-site arrangement; two unrelated `onrender.com` hostnames are not the supported production setup. Cookies belong only to the API host; do not set a Domain attribute or put API credentials in frontend variables.

## 1. Prepare the backend

Create a Render Python web service connected to this repository, with the **repository root** as its root directory. It needs `backend/`, `problems/`, and the operator `tools/` together.

| Setting | Value |
| --- | --- |
| Build command | `pip install -r backend/requirements.txt` |
| Start command | `python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT --workers 1` |
| Python | 3.12 or newer, pinned to your tested version in Render |
| Health check | `/api/health` |
| Instances / workers | **One instance and one process** |
| Persistent disk mount | `/var/data` |

Render persistent disks require a paid service; only files under the disk mount survive restarts/deploys. Keep SQLite and snapshots together under `/var/data/relay`. Follow [Render's persistent disk documentation](https://render.com/docs/disks).

Set backend environment variables:

```dotenv
RELAY_MODE=contest
RELAY_EXECUTOR=managed
RELAY_RUNTIME=/var/data/relay
RELAY_FRONTEND_ORIGIN=https://app.example.com
RELAY_ALLOWED_HOSTS=api.example.com
RELAY_SESSION_SECRET=<one persistent random secret of at least 32 characters>
RELAY_DEV_COOKIES=false
RELAY_TEAM_SESSION_HOURS=4
RELAY_ORGANIZER_SESSION_HOURS=8
RELAY_LOGIN_IP_LIMIT=20
RELAY_LOGIN_NAME_LIMIT=5
RELAY_QUEUE_CAPACITY=10
RELAY_PROVIDER_CONCURRENCY=2
RELAY_REMOTE_JOB_SECONDS=600
JUDGE0_URL=https://your-approved-provider.example
JUDGE0_HEADERS_JSON={"X-Auth-Token":"your-provider-secret"}
JUDGE0_LANGUAGE_IDS_JSON={"python":71,"javascript":63,"cpp":54,"java":62}
```

The language IDs above are **illustrative**, not an approval of those versions at your provider. Obtain `/languages` and `/config_info` from your provider, choose the correct Python/Node/C++17/Java versions, and run the verification command below. Some providers require different authentication headers, which you can specify in `JUDGE0_HEADERS_JSON`. Do not commit these secrets. Keep the same session secret across deployments/restores; changing it invalidates CSRF/session restoration and signed provider approval.

The initial IP login ceiling is 20 per minute, and the name+IP ceiling is 5 per 15 minutes. Tune the IP ceiling during rehearsal if teams share one campus NAT; never trust arbitrary client `X-Forwarded-For` headers. Configure a trusted proxy path if your infrastructure changes the client address. One worker and one active job per team are deliberate safety invariants; queue size, provider concurrency (1–2), session lifetime, login ceilings, and job budget are operator settings.

The service starts without provider approval so organizers can sign in, configure schedules/teams, and publish contests. Code execution stays blocked until verification succeeds. A Render deployment cannot enable practice mode or development cookies.

## 2. Configure the frontend and domains

Create a Render Static Site for this repository:

| Setting | Value |
| --- | --- |
| Root directory | `frontend` |
| Build command | `npm ci && npm run build` |
| Publish directory | `dist` |
| Environment | `VITE_API_BASE_URL=https://api.example.com` |
| Rewrite | `/*` → `/index.html` (Rewrite / status 200) |

Add `app.example.com` to the Static Site and `api.example.com` to the backend Web Service. Configure DNS exactly as Render shows, verify both custom domains, and wait for HTTPS certificates. Render manages TLS certificates for verified custom domains. See [Render custom domains](https://render.com/docs/custom-domains). Rebuild the frontend whenever changing `VITE_API_BASE_URL` because Vite embeds it at build time.

Use precisely `https://app.example.com` for `RELAY_FRONTEND_ORIGIN`, without a path. Only that origin gets credentialed CORS and authenticated mutations. Add every legitimate API host to `RELAY_ALLOWED_HOSTS` explicitly; `RENDER_EXTERNAL_HOSTNAME` is also accepted automatically. Browser requests include credentials and CSRF headers. Never use wildcard CORS or disable secure cookies to work around domain mistakes.

## 3. Bootstrap the organizer

In the Render backend Shell, from the repository root:

```sh
python tools/create_organizer.py --runtime /var/data/relay --username organizer
```

Enter a password of at least 12 characters when prompted. Running it again for the same username resets the password and revokes its old organizer sessions. Passwords are not accepted as command-line arguments or stored as plaintext.

Open `https://app.example.com/organizer/login`. Create an event, set the Asia/Manila start, and choose hours/minutes (default **3 hours 30 minutes**). Register the 4–5 teams. Copy each one-time join code and distribute it privately. Forgotten codes require rotation. Session reset revokes the old browser without changing the code; rotation revokes it and changes the code.

## 4. Verify the managed provider before executing

Choose a provider capable of the real packages: up to 8 MiB stdin, 2 MiB stdout, 5 seconds execution, and enforced 256 MB memory with disabled network. The backend requests these limits and independently compares outputs. It never reduces cases or falls back to local subprocesses. Consult the [Judge0 API contract](https://ce.judge0.com/) and your provider's quotas/version catalog.

Run this **only when ready to consume provider executions**:

Perform verification during staging with team access closed and no other provider work running. Do not run the verification CLI alongside a live contest worker consuming provider executions.

```sh
python tools/verify_managed_provider.py --runtime /var/data/relay --confirm-live
```

It runs all 116 official cases across four languages (464 executions) plus five isolation/size probes, about **469 executions** when all succeed. Source and case input are sent to the provider; expected outputs stay in this backend. A signed approval receipt is saved on the disk only after successful verification. Receipt validity depends on the provider configuration and the exact approved judging content. Published contests continue using their approved frozen content if repository content later changes. Changing provider configuration requires verification again.

Compilation may repeat for each case. Five simultaneous formatter recordings need **325 executions**, before sample/custom runs, rehearsals, and later attempts. Confirm quotas, supported limits, queued execution lifetime, HTTP payload bounds, and sustained capacity; a free/demo endpoint is not presumed adequate. Run staging load tests against your purchased capacity. Requests use bounded polling, with a default ten-minute remote-job budget. Outages, throttling, malformed results, unsupported limits, or ambiguous creation produce incomplete infrastructure assessments. A provider creation whose delivery cannot be reconciled is never blindly resubmitted.

An unresolved execution places the provider on a persistent hold, preventing fresh executions from accumulating beyond the concurrency limit. Reconcile or cancel outstanding executions in the provider's console, then rerun verification with **both** `--confirm-live` and `--confirm-provider-drained`. Do not clear the hold while remote work may still be running. The affected attempt remains an immutable incomplete assessment; a later recording is a separate attempt.

## 5. Rehearse and publish

1. Rehearse with organizer-only access and temporary team codes. Confirm both custom domains, cookie attributes, exact CORS, expiry, and reset/rejoin in separate browser profiles.
2. Verify backups/restores and all three real packages through the selected provider. Check total quota and five-team responsiveness.
3. Select problem packages and publish the contest. Statements/starters/private cases/rubrics/complexity targets are pinned to the persistent disk. Repository updates cannot change this event. Do not edit snapshot files.
4. Teams may join while waiting. Problems are hidden until the server start time. All share one deadline. Record Submission requires confirmation; retries of uncertain recordings reuse the frozen source/key.
5. After start, confirm deadline extensions in the console; shortening uses the explicit confirmed **End contest now** action. Already admitted work remains eligible when results finish later.
6. After the event, teams retain read-only private history. Organizers inspect all attempts and save manual rubric/complexity reviews. Distinct Accepted problems and official-attempt totals remain separate; no attempt penalty or implicit tie-breaker is added.

The four-hour team session is independent from the event duration. A late expiration requires rejoining; organizer reset is available when an abandoned browser still owns a valid session. Browser-local drafts are namespaced per team/event/problem version/language. Teams should use separate browser profiles/devices because local drafts are readable by someone controlling that browser profile.

## 6. Backup, restore, and roll back

Use the SQLite backup API through the provided command, never copy only a live `.sqlite3` file while WAL writes are active:

```sh
python tools/contest_backup.py backup /var/data/relay /var/data/relay-backup-2026-10-24.zip
python tools/contest_backup.py restore /var/data/relay-backup-2026-10-24.zip /var/data/relay-restored
```

Backup destinations must be new; restoration requires a **new** runtime directory. Backups include a consistent database, immutable pinned content, and provider approval. They contain private submissions/hidden tests/session hashes: download a private copy off the service disk and protect it. Keep environment secrets separately in the operator's secret manager.

Stop team admissions/backend before switching `RELAY_RUNTIME` to a restored directory. Restoration validates database integrity/foreign keys and leaves a blocking `RESTORE_INCOMPLETE` marker if it fails. Never start a partially restored runtime. On successful restart, known provider tokens/case progress resume without a second official attempt; unfinished unowned legacy work becomes interrupted. Practice runs do not survive restart.

Before upgrading an existing schema-2 installation, take a backup. Startup migrates schema 2 to 3 transactionally. If rolling back to code that only supports schema 2, restore the pre-upgrade backup into a new runtime; do not point old code at a schema-3 database. Keep one backend instance/process throughout.

## Local rehearsal and verification

For a local mocked contest rehearsal, run `npm run test:contest` in `frontend`; the test harness uses isolated runtime storage and ports 8001/5174. It cannot be used by production startup and never contacts a real provider.

For manual hosted-mode development, set `RELAY_MODE=contest`, a persistent session secret, exact localhost frontend origin, and `RELAY_DEV_COOKIES=true`. This exception is restricted to local development and rejected on Render. Use a configured/verified provider for actual execution. Local practice remains the default when not running on Render.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s backend/tests -v
.\.venv\Scripts\python.exe tools/verify_demo_solutions.py
cd frontend
npm run test:e2e
npm run test:contest
npm run build
```

No custom domains, paid resources, provider account, or deployment are created by these code changes. Complete the domain/provider/backup rehearsal before opening the scheduled event.
