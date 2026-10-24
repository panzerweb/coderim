import secrets
import sqlite3
import uuid
from types import SimpleNamespace
from fastapi import APIRouter, HTTPException, Query, Request, Response
from .auth import normalized
from .contest_models import Confirmation, ContestEdit, OrganizerLogin, PublishContest, TeamActivity, TeamCreate, TeamJoin
from .models import ReviewRequest, RunRequest, SubmissionRequest
from .storage import now


def routes(app):
    router = APIRouter(prefix='/api')
    def auth(): return app.state.auth
    def store(): return app.state.storage
    def contests(): return app.state.contests
    def organizer(request, mutation=False): return auth().principal(request, 'organizer', mutation)
    def team(request, mutation=False): return auth().principal(request, 'team', mutation)

    def identity(request, mutation=False):
        if request.headers.get('x-relay-role') == 'team':
            return 'team', team(request, mutation)
        if request.headers.get('x-relay-role') == 'organizer':
            return 'organizer', organizer(request, mutation)
        if request.cookies.get(auth().cookie_name('organizer')):
            try:
                return 'organizer', organizer(request, mutation)
            except HTTPException as error:
                if error.status_code != 401:
                    raise
        return 'team', team(request, mutation)

    def owned(request, key):
        kind, principal = identity(request)
        attempt = store().get(key)
        if not attempt or (kind == 'team' and attempt['team_id'] != principal['team_id']):
            raise HTTPException(404, 'Submission not found')
        return attempt

    def provider_ready(contest_id=None):
        if app.state.executor == 'local':
            return
        provider = app.state.provider
        context = SimpleNamespace(published=lambda: contests().problems(contest_id)) if contest_id else app.state.repository
        if not provider.refresh(context):
            raise HTTPException(503, 'Organizer must verify the managed judge before enabling execution')

    def supports(language):
        if app.state.executor == 'local':
            return app.state.registry.status[language]['available']
        provider=app.state.provider
        return provider.supports(language) if hasattr(provider,'supports') else provider.status[language]['available']

    @router.get('/contest')
    def current_contests():
        return [c for c in contests().list() if c['phase'] != 'draft']

    @router.post('/teams/join')
    def join(data: TeamJoin, request: Request, response: Response):
        auth().origin(request); auth().throttle(request, data.contest_id + ':' + data.team_name, 'team')
        with store().lock:
            row = store().db.execute('SELECT * FROM teams WHERE contest_id=? AND normalized_name=?',
                (data.contest_id, normalized(data.team_name))).fetchone()
            contest = store().db.execute('SELECT published FROM contests WHERE id=?', (data.contest_id,)).fetchone()
        valid = auth().verify(row['join_code_hash'] if row else auth().dummy, data.join_code)
        if not valid or not row or not row['is_active'] or not contest or not contest['published']:
            raise HTTPException(401, 'Invalid team credentials or contest access')
        csrf = auth().issue('team', row['id'], response, row['join_code_hash'])
        auth().audit('team_joined', row['id'])
        return {'team_id': row['id'], 'team_name': row['name'], 'contest_id': row['contest_id'], 'csrf_token': csrf}

    @router.get('/teams/me')
    def me(request: Request):
        principal = team(request)
        return {'team_id': principal['team_id'], 'team_name': principal['team_name'], 'contest_id': principal['contest_id'],
            'csrf_token': principal['csrf_token'], 'expires_at': principal['expires_at'],
            'contest': contests().public(contests().get(principal['contest_id'])),
            'metrics': store().metrics(principal['team_id'], principal['contest_id'])}

    @router.post('/teams/logout')
    def logout(request: Request, response: Response): return auth().logout(request, response, 'team')

    @router.post('/organizer/login')
    def admin_login(data: OrganizerLogin, request: Request, response: Response):
        auth().origin(request); auth().throttle(request, data.username, 'organizer')
        with store().lock:
            row = store().db.execute('SELECT * FROM organizers WHERE username=?', (normalized(data.username),)).fetchone()
        valid = auth().verify(row['password_hash'] if row else auth().dummy, data.password)
        if not valid or not row or not row['is_active']:
            raise HTTPException(401, 'Invalid organizer credentials')
        csrf = auth().issue('organizer', row['id'], response, row['password_hash'])
        auth().audit('organizer_joined', row['id'], row['id'])
        return {'username': row['username'], 'csrf_token': csrf}

    @router.get('/organizer/me')
    def admin_me(request: Request):
        principal = organizer(request)
        return {'username': principal['username'], 'csrf_token': principal['csrf_token']}

    @router.post('/organizer/logout')
    def admin_logout(request: Request, response: Response): return auth().logout(request, response, 'organizer')

    @router.get('/problems')
    def catalog(request: Request):
        kind, principal = identity(request)
        if kind == 'organizer':
            return [p.catalog() for p in app.state.repository.published()]
        contests().visible(principal['contest_id'])
        return [p.catalog() for p in contests().problems(principal['contest_id'])]

    @router.get('/problems/{problem_id}')
    def problem(problem_id: str, request: Request):
        kind, principal = identity(request)
        if kind == 'organizer':
            p = app.state.repository.get(problem_id)
            if not p: raise HTTPException(404, 'Problem not found')
        else:
            contests().visible(principal['contest_id'])
            p = contests().problem(principal['contest_id'], problem_id)
        return p.public()

    @router.get('/languages')
    def languages(request: Request):
        kind, principal = identity(request)
        if app.state.executor == 'local':
            return app.state.registry.public()
        context = SimpleNamespace(published=lambda: contests().problems(principal['contest_id'])) if kind == 'team' else app.state.repository
        ready=app.state.provider.refresh(context)
        return [{**item,'available':bool(ready and supports(item['id'])),
            'reason':'' if ready and supports(item['id']) else 'Managed provider verification is required for this contest'} for item in app.state.provider.public()]

    def enqueue(data, request, mode):
        principal = team(request, True)
        # Idempotent replay must still succeed after the deadline or while the
        # provider is unavailable; no new work is admitted by that path.
        key = request.headers.get('idempotency-key')
        if mode == 'submit' and key:
            with store().lock:
                exists = store().db.execute('SELECT id FROM attempts WHERE team_id=? AND contest_id=? AND idempotency_key=?',
                    (principal['team_id'], principal['contest_id'], key)).fetchone()
            if exists:
                return app.state.jobs.enqueue(data, None, mode, principal, key)
        contests().active(principal['contest_id'])
        provider_ready(principal['contest_id'])
        p = contests().problem(principal['contest_id'], data.problem_id)
        if data.problem_version != p.meta.version:
            raise HTTPException(409, 'Reload the pinned problem version')
        if not supports(data.language):
            raise HTTPException(422, 'This language toolchain is unavailable')
        if len(data.code.encode()) > p.meta.limits.source_bytes or (isinstance(data, RunRequest) and len(data.stdin.encode()) > p.meta.limits.stdin_bytes):
            raise HTTPException(413, 'Source or custom input exceeds this problem’s byte limit')
        return app.state.jobs.enqueue(data, p, mode, principal, key)

    @router.post('/runs', status_code=202)
    @router.post('/code/run', status_code=202)
    def run(data: RunRequest, request: Request): return enqueue(data, request, data.mode)

    @router.post('/submissions', status_code=202)
    def submit(data: SubmissionRequest, request: Request): return enqueue(data, request, 'submit')

    @router.get('/submissions/me')
    def history(request: Request, limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0)):
        principal = team(request)
        return store().owned_history(principal['team_id'], principal['contest_id'], limit, offset)

    @router.get('/submissions/{attempt_id}')
    @router.get('/attempts/{attempt_id}')
    def detail(attempt_id: str, request: Request): return owned(request, attempt_id)

    @router.get('/attempts')
    def compatibility_history(request: Request, problem_id: str, problem_version: int, language: str, limit: int = Query(200, ge=1, le=200)):
        kind, principal = identity(request)
        if kind == 'organizer':
            return store().list(problem_id, problem_version, language, limit)
        with store().lock:
            rows = store().db.execute('''SELECT * FROM attempts WHERE team_id=? AND contest_id=? AND problem_id=?
                AND problem_version=? AND language=? ORDER BY created_at DESC LIMIT ?''',
                (principal['team_id'], principal['contest_id'], problem_id, problem_version, language, limit)).fetchall()
            return [store()._decode(row, False) for row in rows]

    @router.get('/jobs/{job_id}')
    def job(job_id: str, request: Request):
        kind, principal = identity(request)
        result = app.state.jobs.get(job_id, principal.get('team_id'), organizer=kind == 'organizer')
        if result is None: raise HTTPException(404, 'Job not found')
        return result

    @router.put('/attempts/{attempt_id}/review')
    def review(attempt_id: str, data: ReviewRequest, request: Request):
        principal = organizer(request, True)
        try:
            result = store().review(attempt_id, data)
        except KeyError: raise HTTPException(404, 'Submission not found')
        except ValueError as error: raise HTTPException(409, str(error))
        auth().audit('submission_reviewed', attempt_id, principal['organizer_id'])
        return result

    @router.get('/organizer/contests')
    def admin_contests(request: Request): organizer(request); return contests().list()

    @router.post('/organizer/contests', status_code=201)
    def create_contest(data: ContestEdit, request: Request):
        principal = organizer(request, True)
        return contests().edit(data, principal['organizer_id'])

    @router.put('/organizer/contests/{contest_id}')
    def edit_contest(contest_id: str, data: ContestEdit, request: Request):
        principal = organizer(request, True); contests().get(contest_id)
        return contests().edit(data, principal['organizer_id'], contest_id)

    @router.post('/organizer/contests/{contest_id}/publish')
    def publish(contest_id: str, data: PublishContest, request: Request):
        principal = organizer(request, True)
        return contests().publish(contest_id, data.problem_ids, principal['organizer_id'])

    @router.post('/organizer/contests/{contest_id}/start')
    def start(contest_id: str, data: Confirmation, request: Request):
        principal = organizer(request, True)
        if not data.confirm:
            raise HTTPException(422, 'Confirmation is required')
        return contests().start(contest_id, principal['organizer_id'])

    @router.post('/organizer/contests/{contest_id}/end')
    def end(contest_id: str, data: Confirmation, request: Request):
        principal = organizer(request, True)
        if not data.confirm: raise HTTPException(422, 'Confirmation is required')
        return contests().end(contest_id, principal['organizer_id'])

    @router.get('/organizer/teams')
    def teams(contest_id: str, request: Request):
        organizer(request)
        with store().lock:
            rows = store().db.execute('SELECT id,name,is_active,contest_id,created_at FROM teams WHERE contest_id=? ORDER BY name', (contest_id,)).fetchall()
        return [dict(row) | {'metrics': store().metrics(row['id'], contest_id)} for row in rows]

    @router.post('/organizer/contests/{contest_id}/teams', status_code=201)
    def create_team(contest_id: str, data: TeamCreate, request: Request):
        principal = organizer(request, True); contests().get(contest_id)
        name = data.name.strip()
        if not name: raise HTTPException(422, 'Team name is required')
        code = secrets.token_urlsafe(24); hashed = auth().hasher.hash(code); key = str(uuid.uuid4())
        try:
            with store().lock, store().db:
                store().db.execute('INSERT INTO teams VALUES(?,?,?,?,?,?,?)', (key, contest_id, name, normalized(name), hashed, 1, now()))
        except sqlite3.IntegrityError: raise HTTPException(409, 'This team name is already registered in the contest')
        auth().audit('team_created', key, principal['organizer_id'])
        return {'id': key, 'name': name, 'join_code': code}

    def find_team(key):
        with store().lock:
            row = store().db.execute('SELECT id FROM teams WHERE id=?', (key,)).fetchone()
        if not row: raise HTTPException(404, 'Team not found')

    @router.post('/organizer/teams/{team_id}/reset-session')
    def reset_session(team_id: str, request: Request):
        principal = organizer(request, True); find_team(team_id)
        with store().lock, store().db:
            store().db.execute('UPDATE sessions SET revoked_at=? WHERE team_id=? AND revoked_at IS NULL', (now(), team_id))
        auth().audit('team_session_reset', team_id, principal['organizer_id'])
        return {'reset': True}

    @router.post('/organizer/teams/{team_id}/rotate-code')
    def rotate_code(team_id: str, request: Request):
        principal = organizer(request, True); find_team(team_id)
        code = secrets.token_urlsafe(24); hashed = auth().hasher.hash(code)
        with store().lock, store().db:
            store().db.execute('UPDATE teams SET join_code_hash=? WHERE id=?', (hashed, team_id))
            store().db.execute('UPDATE sessions SET revoked_at=? WHERE team_id=? AND revoked_at IS NULL', (now(), team_id))
        auth().audit('team_code_rotated', team_id, principal['organizer_id'])
        return {'join_code': code}

    @router.put('/organizer/teams/{team_id}')
    def activity(team_id: str, data: TeamActivity, request: Request):
        principal = organizer(request, True); find_team(team_id)
        with store().lock, store().db:
            store().db.execute('UPDATE teams SET is_active=? WHERE id=?', (int(data.is_active), team_id))
            if not data.is_active:
                store().db.execute('UPDATE sessions SET revoked_at=? WHERE team_id=? AND revoked_at IS NULL', (now(), team_id))
        auth().audit('team_activity_changed', team_id, principal['organizer_id'], {'active': data.is_active})
        return {'is_active': data.is_active}

    @router.get('/organizer/submissions')
    def all_submissions(request: Request, contest_id: str | None = None, team_id: str | None = None,
                        limit: int = Query(100, ge=1, le=200), offset: int = Query(0, ge=0)):
        organizer(request); return store().owned_history(team_id=team_id, contest_id=contest_id, limit=limit, offset=offset)

    @router.get('/organizer/provider')
    def provider_status(request: Request):
        organizer(request)
        if app.state.executor == 'local':
            return {'executor':'local', 'verified':True, 'on_hold':False, 'languages':app.state.registry.public()}
        ready = app.state.provider.refresh(app.state.repository)
        return {'executor':'managed', 'verified': ready, 'on_hold': bool(getattr(app.state.provider, 'hold_file', None) and app.state.provider.hold_file.exists()), 'languages': app.state.provider.public()}

    @router.get('/organizer/audit')
    def audit(request: Request):
        organizer(request)
        with store().lock:
            return [dict(row) for row in store().db.execute('SELECT * FROM audit_events ORDER BY id DESC LIMIT 200')]

    return router
