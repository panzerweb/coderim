# Run a team contest without Judge0

The original executor runs the tests and calculates correctness. Team login, official source snapshots, results, reviews, and private history use SQLite. No provider account, API key, or verification command is needed for this workflow.

## Start locally on Windows

From PowerShell in the project directory:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\start-contest.ps1
```

Setup is needed the first time or after dependency/source updates. Subsequent starts only need the second command. Stop any old server on port 8000 with Ctrl+C first.

On the first start, the terminal asks you to choose an organizer username and enter a password twice (at least 12 characters). Subsequent starts reuse that account. The launcher generates and saves a session secret privately in `.runtime/session-secret.txt`; you no longer need to type environment settings or regenerate a secret. If your existing database already has an organizer, use its existing credentials. To reset a forgotten organizer password, run `.\.venv\Scripts\python.exe tools/create_organizer.py --username organizer`.

Open [organizer login](http://127.0.0.1:8000/organizer/login). Keep the terminal running; Ctrl+C stops the server. The launcher always selects the original local executor and binds to loopback. It does not contact Judge0 even if old provider variables exist in your terminal.

## Organizer walkthrough

1. Sign in and click **New contest**.
2. Enter the name, a future start date/time in **Asia/Manila**, and a duration in hours/minutes (default 3:30). Click **Create contest** to save the draft.
3. Select the problem checkboxes under **Problems to freeze** and click **Publish contest**, then confirm. This freezes the selected statements, tests, limits, rubric, and complexity targets. Publication does not need a provider.
4. Under **Teams**, enter a team name and click **Create team**. Copy the generated join code immediately; it is shown once. Repeat for each team. Codes belong to a particular team and contest; there is no shared all-team password.
5. Teams can join before the event and wait. The event starts automatically at the scheduled time. To begin earlier, click **Start contest now** and confirm; this begins the full configured duration immediately for everyone. An active timer cannot be reset by pressing Start again.
6. During the event, you can extend its deadline through **Save schedule**, or confirm **End contest now**. Recordings already admitted before the deadline remain eligible while judging finishes.

## Team walkthrough

1. Use a separate browser profile/private window for each team and open [team join](http://127.0.0.1:8000/join).
2. Select the published contest and enter the team name and its private join code. One active browser session is allowed per team; tabs can share it.
3. Wait until the start, then open the problem library and choose a problem.
4. Write a complete program in an installed language. **Run Code** checks samples; **Custom input** executes your own input. Neither adds an official history entry.
5. Click **Record Submission** and confirm. The app saves that exact source, team, contest, problem/version, language, and timestamp, then runs the complete official suite and saves the scores/results.
6. Open **History** to view your team's attempts and saved source. Other teams' records are inaccessible. After the deadline, history and feedback remain readable while new executions/recordings are disabled.

The local page works on the organizer's computer. `127.0.0.1` on a different computer refers to that other computer. For teams using separate physical devices, use the HTTPS deployment described below rather than distributing a localhost URL.

## Judge walkthrough

The organizer console lists each submission with its team name, problem, language, date, and verdict, with pagination. Select one to see its immutable source, automated category/requirement evidence, and reference complexity. Save the human readability/technical ratings, rationale, and optional complexity analysis there. Teams can read their feedback but cannot edit reviews. **All / legacy submissions** includes historical unowned records for organizers only.

Distinct solved problems count once across repeated attempts and languages. All official attempts remain recorded, including wrong/failed attempts. Acceptance still requires every official test to pass; the assessment weights remain 50/20/15/15.

## Execution and deployment

Python uses the project's virtual environment. Install Node, a JDK, and/or `g++` for other languages; unavailable languages are disabled individually and do not prevent contest publication. The 256 MB local memory target remains unenforced. This is the existing trusted-code executor, with time/output limits and process cleanup, rather than a security sandbox.

For provider-free Render deployment, the included backend Dockerfile supplies Python, Node, Java, and C++. The frontend remains a separate Static Site. Follow [Render deployment](hosted-contests.md). Public local execution requires the explicit trusted-code setting; the container runs the service as a non-root user but does not isolate participant programs from the API/database. A public untrusted-code service still needs an isolated execution system. Judge0 remains an optional executor, not a requirement for contest management.
