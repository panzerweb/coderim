"""Bootstrap/reset an organizer locally; credentials are never command arguments."""
import argparse
import getpass
import os
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.auth import Auth
from app.storage import Storage

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', type=Path, default=Path(os.getenv('RELAY_RUNTIME', ROOT / '.runtime')))
    parser.add_argument('--username', default='organizer')
    args = parser.parse_args()
    password = getpass.getpass('Organizer password (at least 12 characters): ')
    if password != getpass.getpass('Confirm password: '):
        raise SystemExit('Passwords do not match')
    store = Storage(args.runtime / 'history.sqlite3', resume_owned=True)
    try:
        Auth(store, 'bootstrap-not-a-session-secret', set()).create_organizer(args.username, password)
        print('Organizer credentials saved; previous organizer sessions were revoked.')
    finally:
        store.close()
