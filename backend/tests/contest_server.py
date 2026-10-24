"""Browser-test harness only. Never used by production startup."""
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'backend'))
from app.main import create_app
from app.problems import Repository
from hosted_support import FakeProvider

if os.getenv('RELAY_TEST_SERVER')!='yes':
    raise RuntimeError('This harness is only for isolated browser tests')
local = os.getenv('RELAY_TEST_EXECUTOR') == 'local'
app=create_app(mode='contest',executor='local' if local else 'managed',
    provider=None if local else FakeProvider(Repository(ROOT/'problems')),
    session_secret='browser-test-secret-do-not-use-in-production',secure_cookies=False,
    frontend_origin='http://127.0.0.1:5174')
original=app.router.lifespan_context
@asynccontextmanager
async def lifespan(application):
    async with original(application):
        application.state.auth.create_organizer('test-organizer','browser-test-password')
        yield
app.router.lifespan_context=lifespan
