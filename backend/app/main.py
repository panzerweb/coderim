import logging
import os
import queue
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit
from fastapi import APIRouter, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from starlette.middleware.trustedhost import TrustedHostMiddleware
from .jobs import Jobs
from .judge import Judge
from .languages import Registry
from .models import MAX_REQUEST_BYTES, ReviewRequest, RunRequest, SubmissionRequest
from .problems import Repository
from .storage import Storage


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ORIGINS = {"http://127.0.0.1:5173", "http://localhost:5173", "http://127.0.0.1:8000", "http://localhost:8000"}


class RequestGuard:
    def __init__(self, app, origins):
        self.app, self.origins = app, origins

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["method"] not in ("POST", "PUT", "PATCH", "DELETE"):
            return await self.app(scope, receive, send)
        headers = dict(scope["headers"])
        origin = headers.get(b"origin", b"").decode()
        if (origin and origin not in self.origins) or not headers.get(b"content-type", b"").startswith(b"application/json"):
            return await JSONResponse({"detail": "Mutation requests require JSON and an approved local origin"}, status_code=403)(scope, receive, send)
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > MAX_REQUEST_BYTES:
                return await JSONResponse({"detail": "Request body exceeds limit"}, status_code=413)(scope, receive, send)
            body.extend(chunk)
            if not message.get("more_body"):
                break
        delivered = False
        async def bounded_receive():
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()
        await self.app(scope, bounded_receive, send)


def create_app(problem_root: Path | None = None, runtime: Path | None = None, registry=None,
               job_budget=120, queue_capacity=10, retention=3600, mode=None, provider=None,
               session_secret=None, secure_cookies=None, frontend_origin=None, executor=None):
    problem_root = problem_root or Path(os.environ.get("RELAY_PROBLEMS", ROOT / "problems"))
    runtime = runtime or Path(os.environ.get("RELAY_RUNTIME", ROOT / ".runtime"))
    mode = mode or os.environ.get('RELAY_MODE', 'contest' if os.environ.get('RENDER') else 'practice')
    if mode not in ('practice', 'contest'):
        raise ValueError('RELAY_MODE must be practice or contest')
    executor = (executor or ('managed' if provider is not None else os.getenv('RELAY_EXECUTOR',
        'managed' if os.getenv('RENDER') else 'local'))) if mode == 'contest' else 'local'
    if executor not in ('local', 'managed'):
        raise ValueError('RELAY_EXECUTOR must be local or managed')
    if os.environ.get('RENDER') and mode != 'contest':
        raise ValueError('Render deployments must use isolated contest mode')
    dev_cookies = secure_cookies is False or os.getenv('RELAY_DEV_COOKIES') == 'true'
    if os.environ.get('RENDER') and dev_cookies:
        raise ValueError('Development cookies are restricted to local development')
    frontend_origin = frontend_origin or os.environ.get('RELAY_FRONTEND_ORIGIN')
    if dev_cookies and frontend_origin and urlsplit(frontend_origin).hostname not in ('localhost','127.0.0.1','::1'):
        raise ValueError('Development cookies only support a localhost frontend')
    if mode == 'contest' and executor == 'local' and (os.getenv('RENDER') or not dev_cookies):
        if os.getenv('RELAY_TRUSTED_LOCAL_EXECUTION') != 'true':
            raise ValueError('Public local execution requires RELAY_TRUSTED_LOCAL_EXECUTION=true for a trusted-code event')
    origins = set(DEFAULT_ORIGINS) if mode == 'practice' or dev_cookies else set()
    if frontend_origin:
        origins.add(frontend_origin.rstrip('/'))

    @asynccontextmanager
    async def lifespan(app):
        if (runtime / 'RESTORE_INCOMPLETE').exists():
            raise RuntimeError('Runtime restore is incomplete; restore a verified backup into a new directory')
        app.state.repository = Repository(problem_root)
        for folder, error in app.state.repository.errors.items():
            logging.error("Invalid problem %s: %s", folder, error)
        app.state.executor = executor
        app.state.storage = Storage(runtime / "history.sqlite3", resume_owned=mode == 'contest' and executor == 'managed')
        if mode == 'contest':
            from .auth import Auth
            from .contests import Contests
            from .hosted_jobs import HostedJobs
            from .remote_judge import Judge0Client, RemoteJudge
            secret = session_secret or os.getenv('RELAY_SESSION_SECRET', '')
            if len(secret) < 32:
                app.state.storage.close()
                raise RuntimeError('Set a persistent RELAY_SESSION_SECRET of at least 32 characters')
            if not dev_cookies and (not frontend_origin or not frontend_origin.startswith('https://')):
                app.state.storage.close()
                raise RuntimeError('Hosted cookies require an explicit HTTPS frontend origin')
            app.state.auth = Auth(app.state.storage, secret, origins, secure=not dev_cookies,
                team_hours=float(os.getenv('RELAY_TEAM_SESSION_HOURS', '4')),
                organizer_hours=float(os.getenv('RELAY_ORGANIZER_SESSION_HOURS', '8')))
            app.state.contests = Contests(app.state.storage, app.state.repository, runtime, app.state.auth)
            app.state.provider = None
            if executor == 'managed':
                app.state.provider = provider or Judge0Client(runtime, secret)
                app.state.provider.refresh(app.state.repository)
                app.state.registry = app.state.provider
                judge = RemoteJudge(app.state.provider, app.state.storage,
                    budget=float(os.getenv('RELAY_REMOTE_JOB_SECONDS', '600')),
                    concurrency=int(os.getenv('RELAY_PROVIDER_CONCURRENCY', '2')))
            else:
                from .local_contest_judge import LocalContestJudge
                app.state.registry = registry or Registry()
                judge = LocalContestJudge(app.state.registry, runtime / 'runs',
                    float(os.getenv('RELAY_LOCAL_JOB_SECONDS', str(job_budget))))
            app.state.jobs = HostedJobs(judge, app.state.storage,
                app.state.contests, capacity=int(os.getenv('RELAY_QUEUE_CAPACITY', str(queue_capacity))), retention=retention)
        else:
            app.state.registry = registry or Registry()
            app.state.jobs = Jobs(Judge(app.state.registry, runtime / "runs", job_budget), app.state.storage,
                capacity=queue_capacity, retention=retention)
        try:
            yield
        finally:
            app.state.jobs.close()
            if mode == 'contest' and app.state.provider is not None:
                app.state.provider.close()
            app.state.storage.close()

    app = FastAPI(title="Code Relay Judge", version="0.1.0", lifespan=lifespan)
    @app.middleware('http')
    async def private_responses(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith('/api/'):
            response.headers['Cache-Control'] = 'no-store'
        return response
    app.add_middleware(RequestGuard, origins=origins)
    app.add_middleware(CORSMiddleware, allow_origins=sorted(origins), allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "X-CSRF-Token", "Idempotency-Key", "X-Relay-Role"], allow_credentials=mode == 'contest')
    
    allowed_hosts = ["localhost", "127.0.0.1", "[::1]"]

    render_hostname = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if render_hostname:
        allowed_hosts.append(render_hostname)
    allowed_hosts.extend(host.strip() for host in os.getenv('RELAY_ALLOWED_HOSTS', '').split(',') if host.strip())

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )
    practice = APIRouter()

    def problem(key):
        p = app.state.repository.get(key)
        if p is None:
            raise HTTPException(404, "Published problem not found")
        return p

    def validate(request):
        p = problem(request.problem_id)
        if p.meta.version != request.problem_version:
            raise HTTPException(409, "Problem version changed; reload the workspace")
        if not app.state.registry.status[request.language]["available"]:
            raise HTTPException(422, "Language toolchain is unavailable")
        if len(request.code.encode()) > p.meta.limits.source_bytes:
            raise HTTPException(413, "Source exceeds the byte limit")
        if isinstance(request, RunRequest) and len(request.stdin.encode()) > p.meta.limits.stdin_bytes:
            raise HTTPException(413, "Custom input exceeds the byte limit")
        return p

    @app.get("/api/health")
    def health():
        if mode == 'contest' and not app.state.jobs.worker.is_alive():
            raise HTTPException(503, 'Judging worker needs restart')
        return {"status": "ok", "execution": "managed" if executor == 'managed' else "trusted-local", "memory_enforced": executor == 'managed'}

    @app.get('/api/config')
    def configuration():
        return {'mode': mode, 'team_contest': mode == 'contest', 'executor': executor, 'memory_enforced': executor == 'managed'}

    @practice.get("/api/problems")
    def catalog():
        return [p.catalog() for p in app.state.repository.published()]

    @practice.get("/api/problems/{problem_id}")
    def detail(problem_id: str):
        return problem(problem_id).public()

    @practice.get("/api/languages")
    def languages():
        return app.state.registry.public()

    def enqueue(request, mode):
        p = validate(request)
        try:
            return app.state.jobs.enqueue(request, p, mode)
        except queue.Full:
            raise HTTPException(429, "Judge queue is full; try again shortly", headers={"Retry-After": "2"})

    @practice.post("/api/runs", status_code=202)
    def run(request: RunRequest):
        return enqueue(request, request.mode)

    @practice.post("/api/submissions", status_code=202)
    def submit(request: SubmissionRequest):
        return enqueue(request, "submit")

    @practice.get("/api/jobs/{job_id}")
    def job(job_id: str):
        result = app.state.jobs.get(job_id)
        if result is None:
            raise HTTPException(404, "Job expired or is unknown; official attempts remain in history")
        return result

    @practice.get("/api/attempts")
    def attempts(problem_id: str, problem_version: int = Query(ge=1), language: str = Query(), limit: int = Query(200, ge=1, le=200)):
        # Historical versions remain queryable even after content changes.
        return app.state.storage.list(problem_id, problem_version, language, limit)

    @practice.get("/api/attempts/{attempt_id}")
    def attempt(attempt_id: str):
        result = app.state.storage.get(attempt_id)
        if result is None:
            raise HTTPException(404, "Attempt not found")
        return result

    @practice.put("/api/attempts/{attempt_id}/review")
    def review(attempt_id: str, request: ReviewRequest):
        try:
            return app.state.storage.review(attempt_id, request)
        except KeyError:
            raise HTTPException(404, "Attempt not found")
        except ValueError as error:
            raise HTTPException(409, str(error))

    if mode == 'contest':
        from .hosted import routes
        app.include_router(routes(app))
    else:
        app.include_router(practice)

    @app.get("/{path:path}", include_in_schema=False)
    def frontend(path: str):
        if path.startswith("api/") or path == "api":
            raise HTTPException(404, "Unknown API endpoint")
        dist = (ROOT / "frontend" / "dist").resolve()
        target = (dist / path).resolve()
        if not target.is_relative_to(dist):
            raise HTTPException(404)
        if target.is_file():
            return FileResponse(target)
        if (dist / "index.html").is_file() and (not path or path.split('/')[0] in ('problems', 'join', 'dashboard', 'history', 'organizer')):
            return FileResponse(dist / "index.html")
        raise HTTPException(404, "Build the frontend or use the Vite development server")

    return app


app = create_app()
