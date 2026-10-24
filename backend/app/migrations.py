"""Schema 3 statements executed in Storage's migration transaction."""
SCHEMA_3 = [
    """CREATE TABLE contests (
        id TEXT PRIMARY KEY, name TEXT NOT NULL, starts_at TEXT NOT NULL, ends_at TEXT NOT NULL,
        timezone TEXT NOT NULL DEFAULT 'Asia/Manila', published INTEGER NOT NULL DEFAULT 0,
        problem_snapshot_json TEXT NOT NULL DEFAULT '[]', created_at TEXT NOT NULL)""",
    """CREATE TABLE teams (
        id TEXT PRIMARY KEY, contest_id TEXT NOT NULL REFERENCES contests(id), name TEXT NOT NULL,
        normalized_name TEXT NOT NULL, join_code_hash TEXT NOT NULL, is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL, UNIQUE(contest_id, normalized_name))""",
    """CREATE TABLE organizers (
        id TEXT PRIMARY KEY, username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL)""",
    """CREATE TABLE sessions (
        id TEXT PRIMARY KEY, team_id TEXT REFERENCES teams(id), organizer_id TEXT REFERENCES organizers(id),
        token_hash TEXT NOT NULL UNIQUE, csrf_hash TEXT NOT NULL, created_at TEXT NOT NULL,
        expires_at TEXT NOT NULL, revoked_at TEXT,
        CHECK ((team_id IS NOT NULL) != (organizer_id IS NOT NULL)))""",
    "CREATE UNIQUE INDEX one_team_session ON sessions(team_id) WHERE team_id IS NOT NULL AND revoked_at IS NULL",
    """CREATE TABLE audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id TEXT, action TEXT NOT NULL,
        target_id TEXT, created_at TEXT NOT NULL, details_json TEXT NOT NULL DEFAULT '{}')""",
    """CREATE TABLE auth_limits (
        key TEXT PRIMARY KEY, window_start REAL NOT NULL, count INTEGER NOT NULL)""",
    """CREATE TABLE provider_cases (
        attempt_id TEXT NOT NULL REFERENCES attempts(id), case_id TEXT NOT NULL,
        token TEXT, state TEXT NOT NULL, result_json TEXT, PRIMARY KEY(attempt_id, case_id))""",
    """CREATE TABLE provider_jobs (
        attempt_id TEXT PRIMARY KEY REFERENCES attempts(id), started_at TEXT NOT NULL,
        budget_seconds REAL NOT NULL)""",
    "ALTER TABLE attempts ADD COLUMN team_id TEXT REFERENCES teams(id)",
    "ALTER TABLE attempts ADD COLUMN contest_id TEXT REFERENCES contests(id)",
    "ALTER TABLE attempts ADD COLUMN idempotency_key TEXT",
    "ALTER TABLE attempts ADD COLUMN request_fingerprint TEXT",
    "ALTER TABLE attempts ADD COLUMN eligible_at TEXT",
    "CREATE UNIQUE INDEX attempt_idempotency ON attempts(team_id, contest_id, idempotency_key)",
    "CREATE INDEX team_history ON attempts(team_id, contest_id, created_at)",
    "CREATE UNIQUE INDEX one_team_job ON attempts(team_id) WHERE team_id IS NOT NULL AND result_json IS NULL",
]
