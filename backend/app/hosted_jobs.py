import hashlib
import json
import logging
import queue
import threading
import time
import uuid
from fastapi import HTTPException
from .models import SubmissionRequest
from .storage import now


class HostedJobs:
    def __init__(self, judge, store, contests, capacity=10, retention=3600):
        if capacity < 1:
            raise ValueError('Queue capacity must be positive')
        self.judge, self.store, self.contests = judge, store, contests
        self.capacity, self.retention = capacity, retention
        self.queue = queue.Queue(maxsize=capacity)
        self.lock = threading.RLock()
        self.stop = threading.Event()
        self.records = {}
        self.active_teams = set()
        with store.lock:
            pending = store.db.execute('SELECT * FROM attempts WHERE team_id IS NOT NULL AND result_json IS NULL ORDER BY created_at').fetchall()
        for row in pending:
            self.records[row['id']] = {'id': row['id'], 'state': 'queued', 'result': None,
                'attempt_id': row['id'], 'team_id': row['team_id'], 'contest_id': row['contest_id']}
            self.active_teams.add(row['team_id'])
        self.worker = threading.Thread(target=self._work, name='contest-judge', daemon=True)
        self.worker.start()
        for row in pending:
            req = SubmissionRequest(problem_id=row['problem_id'], problem_version=row['problem_version'], language=row['language'], code=row['code'])
            self.queue.put((row['id'], req, row['contest_id'], 'submit', ''))

    def enqueue(self, request, problem, mode, team, key=None):
        official = mode == 'submit'
        fingerprint = hashlib.sha256(json.dumps(request.model_dump(), sort_keys=True).encode()).hexdigest()
        with self.lock, self.store.lock:
            if official:
                if not key or len(key) > 128:
                    raise HTTPException(422, 'Record Submission requires an Idempotency-Key')
                prior = self.store.db.execute('SELECT * FROM attempts WHERE team_id=? AND contest_id=? AND idempotency_key=?',
                    (team['team_id'], team['contest_id'], key)).fetchone()
                if prior:
                    if prior['request_fingerprint'] != fingerprint:
                        raise HTTPException(409, 'This idempotency key belongs to different source content')
                    return {'job_id': prior['id'], 'attempt_id': prior['id']}
            # Admission time and the active-window decision use the same clock.
            admitted = now()
            contest = self.contests.get(team['contest_id'])
            from .contests import utc
            if not contest['published'] or not (utc(contest['starts_at']) <= utc(admitted) < utc(contest['ends_at'])):
                raise HTTPException(409, 'The contest is not accepting runs or submissions')
            active_team = self.store.db.execute('SELECT is_active FROM teams WHERE id=?', (team['team_id'],)).fetchone()
            if not active_team or not active_team['is_active']:
                raise HTTPException(401, 'Team is inactive')
            if team['team_id'] in self.active_teams:
                raise HTTPException(409, 'This team already has a judging job in progress')
            if self.stop.is_set() or self.queue.full():
                raise HTTPException(429, 'Judge queue is full; try again shortly', headers={'Retry-After': '2'})
            identifier = str(uuid.uuid4())
            if official:
                self.store.create(identifier, request, problem.meta.rubric.model_dump(),
                    problem.meta.reference_complexity.model_dump() if problem.meta.reference_complexity else None,
                    team_id=team['team_id'], contest_id=team['contest_id'], idempotency_key=key,
                    request_fingerprint=fingerprint, eligible_at=admitted)
            self.records[identifier] = {'id': identifier, 'state': 'queued', 'result': None,
                'attempt_id': identifier if official else None, 'team_id': team['team_id'], 'contest_id': team['contest_id']}
            self.active_teams.add(team['team_id'])
            self.queue.put_nowait((identifier, request, team['contest_id'], mode, getattr(request, 'stdin', '')))
            return {'job_id': identifier, 'attempt_id': identifier if official else None}

    def get(self, key, team_id=None, organizer=False):
        with self.lock:
            for identifier in list(self.records):
                if self.records[identifier].get('finished', float('inf')) < time.monotonic() - self.retention:
                    del self.records[identifier]
            item = self.records.get(key)
            if not item:
                saved = self.store.get(key)
                if saved:
                    item = {'id': key, 'state': saved['status'], 'result': saved['result'],
                        'attempt_id': key, 'team_id': saved['team_id']}
            if not item or (not organizer and item['team_id'] != team_id):
                return None
            return {k: item[k] for k in ('id', 'state', 'result', 'attempt_id')}

    def _work(self):
        while not self.stop.is_set():
            try:
                key, req, contest_id, mode, stdin = self.queue.get(timeout=.1)
            except queue.Empty:
                continue
            official = mode == 'submit'
            def progress(state):
                with self.lock:
                    self.records[key]['state'] = state
                if official:
                    self.store.status(key, state)
            interrupted = False
            try:
                problem = self.contests.problem(contest_id, req.problem_id)
                result = self.judge.run(problem, req.language, req.code, mode, stdin, progress, self.stop,
                    attempt_id=key if official else None)
            except InterruptedError:
                interrupted = True
                result = None
            except Exception:
                result = {'mode': mode, 'verdict': 'Judge Error', 'attempted': 0, 'passed': 0, 'total': 0,
                    'duration_ms': 0, 'cases': [], 'assessment': None, 'diagnostics': '',
                    'incomplete_reason': 'Pinned content or judging is unavailable'}
            try:
                if not interrupted:
                    if official:
                        self.store.complete(key, result)
                    with self.lock:
                        self.records[key].update(state='failed' if result['verdict'] == 'Judge Error' else 'completed',
                            result=result, finished=time.monotonic())
            except Exception:
                logging.exception('Could not persist judging result; admissions stopped until restart')
                self.stop.set()
            finally:
                with self.lock:
                    self.active_teams.discard(self.records[key]['team_id'])
                self.queue.task_done()

    def close(self):
        self.stop.set()
        self.worker.join(timeout=50)
        if self.worker.is_alive():
            raise RuntimeError('Contest judge worker did not stop')
