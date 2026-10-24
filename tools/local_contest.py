"""Start the provider-free local contest, with persistent secrets and first-run setup."""
import getpass
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.auth import Auth
from app.storage import Storage


def prepare(runtime, input_name=input, password=getpass.getpass):
    runtime = Path(runtime)
    if (runtime / 'RESTORE_INCOMPLETE').exists():
        raise RuntimeError('Restore must finish before starting the contest')
    runtime.mkdir(parents=True, exist_ok=True)
    secret_file = runtime / 'session-secret.txt'
    if not secret_file.exists():
        candidate = os.getenv('RELAY_SESSION_SECRET', '')
        secret = candidate if len(candidate) >= 32 else secrets.token_urlsafe(48)
        try:
            with secret_file.open('x', encoding='utf-8') as output:
                output.write(secret)
            secret_file.chmod(0o600)
        except FileExistsError:
            pass
    secret = secret_file.read_text(encoding='utf-8').strip()
    if len(secret) < 32:
        raise RuntimeError('The saved session secret is invalid; restore it from your private backup')
    store = Storage(runtime / 'history.sqlite3', resume_owned=True)
    try:
        if not store.db.execute('SELECT 1 FROM organizers WHERE is_active=1 LIMIT 1').fetchone():
            print('First launch: create your organizer login. No judging provider is needed.')
            username = input_name('Organizer username [organizer]: ').strip() or 'organizer'
            while True:
                value = password('Organizer password (at least 12 characters): ')
                confirmation = password('Confirm password: ')
                if len(value) < 12 or value != confirmation:
                    print('Use at least 12 characters and enter the same password twice.')
                    continue
                Auth(store, secret, set()).create_organizer(username, value)
                break
    finally:
        store.close()
    return secret


def main():
    if os.getenv('RENDER'):
        raise SystemExit('Use the production entrypoint on Render; this launcher binds only to localhost')
    runtime = Path(os.getenv('RELAY_RUNTIME', ROOT / '.runtime')).resolve()
    os.environ.update(RELAY_MODE='contest', RELAY_EXECUTOR='local', RELAY_DEV_COOKIES='true',
        RELAY_FRONTEND_ORIGIN='http://127.0.0.1:8000', RELAY_RUNTIME=str(runtime),
        RELAY_SESSION_SECRET=prepare(runtime))
    print('Organizer: http://127.0.0.1:8000/organizer/login')
    print('Teams:     http://127.0.0.1:8000/join')
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=8000, workers=1)


if __name__ == '__main__':
    main()
