"""Durable source/result snapshots. Reviews never reinterpret the saved rubric."""
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from .models import ReviewRequest
from .migrations import SCHEMA_3


def now():
    return datetime.now(timezone.utc).isoformat()


class Storage:
    def __init__(self, path: Path, resume_owned=False):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.db = sqlite3.connect(path, check_same_thread=False, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("PRAGMA journal_mode=WAL")
        version = self.db.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1, 2, 3):
            self.db.close()
            raise RuntimeError("Unsupported history database version")
        # DDL and the version change share one transaction. Existing snapshots are
        # untouched; migrated attempts have no retroactively assigned target.
        try:
            with self.db:
                self.db.execute("BEGIN IMMEDIATE")
                if version == 0:
                    self.db.execute("""CREATE TABLE attempts (
                    id TEXT PRIMARY KEY, created_at TEXT NOT NULL, problem_id TEXT NOT NULL,
                    problem_version INTEGER NOT NULL, language TEXT NOT NULL, code TEXT NOT NULL,
                    rubric_json TEXT NOT NULL, status TEXT NOT NULL, result_json TEXT,
                    review_json TEXT, complexity_context_json TEXT
                    )""")
                elif version == 1:
                    self.db.execute("ALTER TABLE attempts ADD COLUMN complexity_context_json TEXT")
                self.db.execute("CREATE INDEX IF NOT EXISTS attempt_groups ON attempts(problem_id, problem_version, language, created_at)")
                if version < 3:
                    for statement in SCHEMA_3:
                        self.db.execute(statement)
                self.db.execute("PRAGMA user_version=3")
        except Exception:
            self.db.close()
            raise
        interrupted = json.dumps({"mode": "submit", "verdict": "Judge Error", "attempted": 0,
            "passed": 0, "total": 0, "duration_ms": 0, "cases": [], "assessment": None,
            "diagnostics": "", "incomplete_reason": "Backend restarted before judging completed"})
        self.db.execute("UPDATE attempts SET status='interrupted', result_json=? WHERE result_json IS NULL" +
            (" AND team_id IS NULL" if resume_owned else ""), (interrupted,))
        self.db.commit()

    def create(self, job_id, request, rubric, reference_complexity=None, *, team_id=None, contest_id=None,
               idempotency_key=None, request_fingerprint=None, eligible_at=None):
        with self.lock, self.db:
            self.db.execute("""INSERT INTO attempts
                (id, created_at, problem_id, problem_version, language, code, rubric_json, status, complexity_context_json,
                 team_id, contest_id, idempotency_key, request_fingerprint, eligible_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (job_id, now(), request.problem_id, request.problem_version, request.language,
                 request.code, json.dumps(rubric), "queued",
                 json.dumps(reference_complexity) if reference_complexity is not None else None,
                 team_id, contest_id, idempotency_key, request_fingerprint, eligible_at))

    def status(self, job_id, state):
        with self.lock, self.db:
            self.db.execute("UPDATE attempts SET status=? WHERE id=? AND result_json IS NULL", (state, job_id))

    def complete(self, job_id, result):
        with self.lock, self.db:
            self.db.execute("UPDATE attempts SET status=?, result_json=? WHERE id=? AND result_json IS NULL",
                ("failed" if result["verdict"] == "Judge Error" else "completed", json.dumps(result), job_id))

    def _decode(self, row, include_code=True):
        item = dict(row)
        rubric = json.loads(item.pop("rubric_json"))
        raw_result, raw_review = item.pop("result_json"), item.pop("review_json")
        raw_context = item.pop("complexity_context_json")
        result = json.loads(raw_result) if raw_result else None
        review = json.loads(raw_review) if raw_review else None
        item.update(rubric=rubric, result=result, review=review,
            reference_complexity=json.loads(raw_context) if raw_context else None)
        if result and result.get("assessment") and review:
            a = result["assessment"]
            a["readability"] = sum(review["readability"]) / 4 * 25
            a["technical"] = sum(review["technical"]) / 4 * 25
            a["review_pending"] = False
            if a["complete"]:
                a["final"] = round(sum(a[key] * weight / 100 for key, weight in rubric["weights"].items()), 2)
        if not include_code:
            item.pop("code")
            if result:
                result.pop("cases", None)
                result.pop("diagnostics", None)
        return item

    def get(self, key):
        with self.lock:
            row = self.db.execute("SELECT *, (SELECT name FROM teams WHERE teams.id=attempts.team_id) AS team_name FROM attempts WHERE id=?", (key,)).fetchone()
            return self._decode(row) if row else None

    def list(self, problem_id, version, language, limit=200):
        with self.lock:
            rows = self.db.execute("SELECT * FROM attempts WHERE problem_id=? AND problem_version=? AND language=? ORDER BY created_at DESC, id DESC LIMIT ?",
                (problem_id, version, language, limit)).fetchall()
            return [self._decode(row, False) for row in rows]

    def review(self, key, review: ReviewRequest):
        with self.lock, self.db:
            item = self.get(key)
            if not item:
                raise KeyError(key)
            if not item["result"] or not item["result"].get("assessment"):
                raise ValueError("This attempt has no completed assessment to review")
            data = review.model_dump()
            # Older clients know only rubric ratings. Omission (or null) must
            # preserve an existing source-bound complexity review.
            if data["complexity"] is None:
                data["complexity"] = (item["review"] or {}).get("complexity")
            self.db.execute("UPDATE attempts SET review_json=? WHERE id=?",
                (json.dumps({**data, "updated_at": now()}), key))
            return self.get(key)

    def close(self):
        with self.lock:
            self.db.close()

    def provider_case(self, attempt_id, case_id):
        with self.lock:
            row = self.db.execute("SELECT * FROM provider_cases WHERE attempt_id=? AND case_id=?", (attempt_id, case_id)).fetchone()
            return dict(row) if row else None

    def remote_job(self, attempt_id, budget):
        with self.lock, self.db:
            self.db.execute('INSERT OR IGNORE INTO provider_jobs(attempt_id,started_at,budget_seconds) VALUES(?,?,?)',
                (attempt_id, now(), budget))
            return dict(self.db.execute('SELECT * FROM provider_jobs WHERE attempt_id=?',(attempt_id,)).fetchone())

    def save_provider_case(self, attempt_id, case_id, state, token=None, result=None):
        with self.lock, self.db:
            self.db.execute("""INSERT INTO provider_cases(attempt_id,case_id,state,token,result_json) VALUES(?,?,?,?,?)
                ON CONFLICT(attempt_id,case_id) DO UPDATE SET state=excluded.state,
                token=COALESCE(excluded.token,provider_cases.token),result_json=excluded.result_json""",
                (attempt_id, case_id, state, token, json.dumps(result) if result is not None else None))

    def owned_history(self, team_id=None, contest_id=None, limit=100, offset=0):
        clauses, values = [], []
        if team_id is not None:
            clauses.append('team_id=?'); values.append(team_id)
        if contest_id is not None:
            clauses.append('contest_id=?'); values.append(contest_id)
        where = ' WHERE ' + ' AND '.join(clauses) if clauses else ''
        with self.lock:
            rows = self.db.execute('SELECT *, (SELECT name FROM teams WHERE teams.id=attempts.team_id) AS team_name FROM attempts' + where + ' ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?',
                (*values, limit, offset)).fetchall()
            return [self._decode(row, False) for row in rows]

    def metrics(self, team_id, contest_id):
        with self.lock:
            rows = self.db.execute('SELECT problem_id,result_json FROM attempts WHERE team_id=? AND contest_id=?',
                (team_id, contest_id)).fetchall()
        solved = {r['problem_id'] for r in rows if r['result_json'] and json.loads(r['result_json']).get('verdict') == 'Accepted'}
        return {'solved_problems': len(solved), 'official_attempts': len(rows)}
