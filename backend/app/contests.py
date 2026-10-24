"""Contest scheduling and immutable, private content snapshots."""
import hashlib
import json
import shutil
import uuid
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from fastapi import HTTPException
from .problems import load_problem
from .storage import now


def utc(value):
    return datetime.fromisoformat(value).astimezone(timezone.utc)


class Contests:
    def __init__(self, store, repository, runtime, auth):
        self.store, self.repository, self.runtime, self.auth = store, repository, Path(runtime), auth
        self.publish_lock = threading.Lock()

    def get(self, key):
        with self.store.lock:
            row = self.store.db.execute('SELECT * FROM contests WHERE id=?', (key,)).fetchone()
        if not row:
            raise HTTPException(404, 'Contest not found')
        return dict(row)

    def public(self, contest):
        clock = datetime.now(timezone.utc)
        phase = 'draft' if not contest['published'] else ('waiting' if clock < utc(contest['starts_at']) else 'active' if clock < utc(contest['ends_at']) else 'ended')
        return {k: contest[k] for k in ('id', 'name', 'starts_at', 'ends_at', 'timezone')} | {
            'phase': phase, 'server_time': clock.isoformat(), 'duration_minutes': round((utc(contest['ends_at']) - utc(contest['starts_at'])).total_seconds() / 60)}

    def list(self):
        with self.store.lock:
            rows = self.store.db.execute('SELECT * FROM contests ORDER BY created_at DESC').fetchall()
        return [self.public(dict(row)) for row in rows]

    def edit(self, data, actor, key=None):
        start = data.starts_at.astimezone(timezone.utc)
        end = start + timedelta(minutes=data.duration_minutes)
        key = key or str(uuid.uuid4())
        with self.store.lock, self.store.db:
            existing = self.store.db.execute('SELECT * FROM contests WHERE id=?', (key,)).fetchone()
            if existing and existing['published'] and datetime.now(timezone.utc) >= utc(existing['starts_at']):
                if start != utc(existing['starts_at']) or end < utc(existing['ends_at']):
                    raise HTTPException(409, 'After start, keep the start time and extend the deadline; use End now to close early')
            if existing:
                self.store.db.execute('UPDATE contests SET name=?,starts_at=?,ends_at=?,timezone=? WHERE id=?',
                    (data.name.strip(), start.isoformat(), end.isoformat(), data.timezone, key))
            else:
                self.store.db.execute('INSERT INTO contests(id,name,starts_at,ends_at,timezone,created_at) VALUES(?,?,?,?,?,?)',
                    (key, data.name.strip(), start.isoformat(), end.isoformat(), data.timezone, now()))
        self.auth.audit('contest_schedule_saved', key, actor)
        return self.public(self.get(key))

    def end(self, key, actor):
        self.active(key)
        with self.store.lock, self.store.db:
            self.store.db.execute('UPDATE contests SET ends_at=? WHERE id=?', (now(), key))
        self.auth.audit('contest_ended_early', key, actor)
        return self.public(self.get(key))

    def start(self, key, actor):
        with self.store.lock, self.store.db:
            contest = self.get(key)
            if self.public(contest)['phase'] != 'waiting':
                raise HTTPException(409, 'Only a published waiting contest can be started; an active timer cannot be reset')
            duration = utc(contest['ends_at']) - utc(contest['starts_at'])
            start = datetime.now(timezone.utc)
            self.store.db.execute('UPDATE contests SET starts_at=?,ends_at=? WHERE id=?',
                (start.isoformat(), (start + duration).isoformat(), key))
            self.auth.audit('contest_started_manually', key, actor)
        return self.public(self.get(key))

    def publish(self, key, ids, actor):
        with self.publish_lock:
            return self._publish(key, ids, actor)

    def _publish(self, key, ids, actor):
        contest = self.get(key)
        if contest['published']:
            raise HTTPException(409, 'Published content is immutable; create a new contest to change problems')
        if len(set(ids)) != len(ids):
            raise HTTPException(422, 'Choose each problem once')
        snapshots = []
        destination = self.runtime / 'contests' / key / 'problems'
        destination.mkdir(parents=True, exist_ok=True)
        try:
            for slug in ids:
                p = self.repository.get(slug)
                if p is None:
                    raise HTTPException(422, 'Published problem not found')
                folder = destination / slug
                # Build from already validated in-memory data; do not copy author files or symlinks.
                folder.mkdir(exist_ok=False)
                (folder / 'tests').mkdir(); (folder / 'starters').mkdir()
                metadata = p.meta.model_dump()
                metadata.update(statement_file='statement.md', samples_file='samples.json', tests_manifest='tests/manifest.json', starters={})
                for language, source in p.starters.items():
                    path = f'starters/{language}.txt'
                    (folder / path).write_text(source, encoding='utf-8')
                    metadata['starters'][language] = path
                samples = [s.model_dump() for s in p.samples]
                hidden = []
                for i, case in enumerate(c for c in p.cases if not c.visible):
                    input_file, output_file = f'tests/{i}.in', f'tests/{i}.out'
                    (folder / input_file).write_text(case.stdin, encoding='utf-8', newline='')
                    (folder / output_file).write_text(case.expected, encoding='utf-8', newline='')
                    hidden.append({'id': case.id, 'input_file': input_file, 'output_file': output_file,
                        'category': case.category, 'requirements': list(case.requirements)})
                for name, content in [('problem.json', metadata), ('samples.json', samples), ('tests/manifest.json', {'cases': hidden})]:
                    (folder / name).write_text(json.dumps(content), encoding='utf-8')
                (folder / 'statement.md').write_text(p.statement, encoding='utf-8')
                checked = load_problem(folder)
                checksum = hashlib.sha256()
                for path in sorted(f for f in folder.rglob('*') if f.is_file()):
                    checksum.update(str(path.relative_to(folder)).replace('\\', '/').encode()); checksum.update(path.read_bytes())
                snapshots.append({'id': slug, 'version': checked.meta.version, 'sha256': checksum.hexdigest(), 'title': p.meta.title})
            with self.store.lock, self.store.db:
                self.store.db.execute('UPDATE contests SET published=1,problem_snapshot_json=? WHERE id=? AND published=0',
                    (json.dumps(snapshots), key))
        except Exception:
            # This path is generated below the configured runtime, never participant input.
            if destination.resolve().is_relative_to(self.runtime.resolve()):
                shutil.rmtree(destination, ignore_errors=True)
            raise
        self.auth.audit('contest_published', key, actor, {'problem_ids': ids})
        return self.public(self.get(key))

    def problems(self, key):
        contest = self.get(key)
        return [self.problem(key, p['id']) for p in json.loads(contest['problem_snapshot_json'])]

    def problem(self, key, slug):
        contest = self.get(key)
        context = next((p for p in json.loads(contest['problem_snapshot_json']) if p['id'] == slug), None)
        if not context:
            raise HTTPException(404, 'Contest problem not found')
        folder = self.runtime / 'contests' / key / 'problems' / slug
        checksum = hashlib.sha256()
        for path in sorted(f for f in folder.rglob('*') if f.is_file()):
            checksum.update(str(path.relative_to(folder)).replace('\\', '/').encode()); checksum.update(path.read_bytes())
        if checksum.hexdigest() != context['sha256']:
            raise HTTPException(503, 'Pinned contest content failed its integrity check')
        return load_problem(folder)

    def visible(self, key):
        contest = self.get(key)
        if self.public(contest)['phase'] in ('waiting', 'draft'):
            raise HTTPException(403, 'Problems are revealed when the contest starts')
        return contest

    def active(self, key):
        contest = self.get(key)
        if self.public(contest)['phase'] != 'active':
            raise HTTPException(409, 'The contest is not accepting runs or submissions')
        return contest
