"""Opaque host-only sessions; only hashes of login secrets are persisted."""
import hashlib
import hmac
import os
import secrets
import time
import uuid
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import HTTPException
from .storage import now


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def normalized(value):
    return value.strip().casefold()


class Auth:
    def __init__(self, storage, secret, origins, secure=True, team_hours=4, organizer_hours=8):
        self.store, self.secret, self.origins, self.secure = storage, secret.encode(), origins, secure
        self.team_hours, self.organizer_hours = team_hours, organizer_hours
        self.hasher = PasswordHasher()
        self.dummy = self.hasher.hash(secrets.token_urlsafe(32))

    def cookie_name(self, kind):
        return ('__Host-' if self.secure else '') + 'relay_' + kind

    def origin(self, request):
        if request.headers.get('origin') not in self.origins:
            raise HTTPException(403, 'Request origin is not allowed')

    def audit(self, action, target=None, actor=None, details=None):
        with self.store.lock, self.store.db:
            self.store.db.execute('INSERT INTO audit_events(actor_id,action,target_id,created_at,details_json) VALUES(?,?,?,?,?)',
                (actor, action, target, now(), __import__('json').dumps(details or {})))

    def throttle(self, request, name, kind):
        ip = request.client.host if request.client else 'unknown'
        # Do not trust a caller-supplied X-Forwarded-For header.
        keys = [(digest(f'{kind}:ip:{ip}'), int(os.getenv('RELAY_LOGIN_IP_LIMIT', '20')), 60),
            (digest(f'{kind}:name:{ip}:{normalized(name)}'), int(os.getenv('RELAY_LOGIN_NAME_LIMIT', '5')), 900)]
        clock = time.time()
        with self.store.lock, self.store.db:
            for key, limit, window in keys:
                row = self.store.db.execute('SELECT * FROM auth_limits WHERE key=?', (key,)).fetchone()
                start, count = (row['window_start'], row['count']) if row and clock - row['window_start'] < window else (clock, 0)
                if count >= limit:
                    raise HTTPException(429, 'Too many login attempts; try again later', headers={'Retry-After': str(window)})
                self.store.db.execute('INSERT INTO auth_limits VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET window_start=excluded.window_start,count=excluded.count',
                    (key, start, count + 1))
            self.store.db.execute('DELETE FROM auth_limits WHERE window_start<?', (clock - 86400,))

    def verify(self, hashed, value):
        try:
            return self.hasher.verify(hashed, value)
        except (VerificationError, InvalidHashError):
            return False

    def csrf(self, token):
        return hmac.new(self.secret, token.encode(), hashlib.sha256).hexdigest()

    def issue(self, kind, principal_id, response, credential_hash=None):
        token = secrets.token_urlsafe(32)
        csrf = self.csrf(token)
        created = datetime.now(timezone.utc)
        lifetime = timedelta(hours=self.team_hours if kind == 'team' else self.organizer_hours)
        with self.store.lock, self.store.db:
            table, field = ('teams', 'join_code_hash') if kind == 'team' else ('organizers', 'password_hash')
            current = self.store.db.execute(f'SELECT is_active,{field} AS secret_hash FROM {table} WHERE id=?', (principal_id,)).fetchone()
            if not current or not current['is_active'] or (credential_hash and current['secret_hash'] != credential_hash):
                raise HTTPException(401, 'Credentials or access changed; sign in again')
            if kind == 'team':
                self.store.db.execute('UPDATE sessions SET revoked_at=? WHERE team_id=? AND revoked_at IS NULL AND expires_at<=?',
                    (created.isoformat(), principal_id, created.isoformat()))
                active = self.store.db.execute('SELECT id FROM sessions WHERE team_id=? AND revoked_at IS NULL', (principal_id,)).fetchone()
                if active:
                    raise HTTPException(409, 'This team already has an active session. Ask the organizer to reset it.')
            self.store.db.execute('INSERT INTO sessions(id,team_id,organizer_id,token_hash,csrf_hash,created_at,expires_at) VALUES(?,?,?,?,?,?,?)',
                (str(uuid.uuid4()), principal_id if kind == 'team' else None, principal_id if kind == 'organizer' else None,
                 digest(token), digest(csrf), created.isoformat(), (created + lifetime).isoformat()))
        response.set_cookie(self.cookie_name(kind), token, max_age=int(lifetime.total_seconds()), httponly=True,
            secure=self.secure, samesite='strict', path='/')
        return csrf

    def principal(self, request, kind, mutation=False):
        token = request.cookies.get(self.cookie_name(kind), '')
        if not token:
            raise HTTPException(401, 'Sign in to continue')
        with self.store.lock:
            row = self.store.db.execute('''SELECT s.*,t.contest_id,t.name AS team_name,t.is_active AS team_active,
                o.username,o.is_active AS organizer_active FROM sessions s
                LEFT JOIN teams t ON t.id=s.team_id LEFT JOIN organizers o ON o.id=s.organizer_id
                WHERE s.token_hash=? AND s.revoked_at IS NULL AND s.expires_at>?''', (digest(token), now())).fetchone()
        if not row or not row[kind + '_id'] or not row[kind + '_active']:
            raise HTTPException(401, 'Session expired or revoked; sign in again')
        csrf = self.csrf(token)
        if not hmac.compare_digest(digest(csrf), row['csrf_hash']):
            raise HTTPException(401, 'Session configuration changed; ask the organizer to reset your session')
        if mutation:
            self.origin(request)
            if not hmac.compare_digest(request.headers.get('x-csrf-token', ''), csrf):
                raise HTTPException(403, 'CSRF token is missing or invalid')
        return {**dict(row), 'csrf_token': csrf}

    def logout(self, request, response, kind):
        principal = self.principal(request, kind, True)
        with self.store.lock, self.store.db:
            self.store.db.execute('UPDATE sessions SET revoked_at=? WHERE id=?', (now(), principal['id']))
        response.delete_cookie(self.cookie_name(kind), path='/', secure=self.secure, httponly=True, samesite='strict')
        return {'logged_out': True}

    def create_organizer(self, username, password):
        username = normalized(username)
        if not username or len(password) < 12:
            raise ValueError('Use a username and a password of at least 12 characters')
        hashed = self.hasher.hash(password)
        with self.store.lock, self.store.db:
            existing = self.store.db.execute('SELECT id FROM organizers WHERE username=?', (username,)).fetchone()
            key = existing['id'] if existing else str(uuid.uuid4())
            if existing:
                self.store.db.execute('UPDATE organizers SET password_hash=?,is_active=1 WHERE id=?', (hashed, key))
                self.store.db.execute('UPDATE sessions SET revoked_at=? WHERE organizer_id=? AND revoked_at IS NULL', (now(), key))
            else:
                self.store.db.execute('INSERT INTO organizers VALUES(?,?,?,?,?)', (key, username, hashed, 1, now()))
        self.audit('organizer_credentials_updated', key)
        return key
