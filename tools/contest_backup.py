"""Consistent SQLite + pinned-content backup; restore only into a new runtime folder."""
import argparse
import json
import shutil
import sqlite3
import stat
import tempfile
import zipfile
from pathlib import Path


def backup(runtime: Path, destination: Path):
    runtime = runtime.resolve()
    if not (runtime / 'history.sqlite3').is_file() or (runtime / 'RESTORE_INCOMPLETE').exists():
        raise ValueError('A complete existing runtime database is required')
    if destination.exists():
        raise ValueError('Backup destination must be new')
    with tempfile.TemporaryDirectory() as temporary:
        copied = Path(temporary) / 'history.sqlite3'
        source = sqlite3.connect(runtime / 'history.sqlite3')
        target = sqlite3.connect(copied)
        try:
            source.backup(target)
        finally:
            target.close(); source.close()
        with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(copied, 'history.sqlite3')
            for file in (runtime / 'contests').rglob('*'):
                if file.is_symlink() or not file.resolve().is_relative_to(runtime):
                    raise ValueError('Unsafe runtime snapshot path')
                if file.is_file(): archive.write(file, file.relative_to(runtime).as_posix())
            for name in ('provider-verification.json','provider-hold.json','session-secret.txt'):
                if (runtime / name).is_file():
                    archive.write(runtime / name, name)


def restore(source: Path, destination: Path):
    destination = destination.resolve()
    if destination.exists():
        raise ValueError('Restore destination must be a new runtime directory; stop the backend before switching runtimes')
    with zipfile.ZipFile(source) as archive:
        names = set()
        for item in archive.infolist():
            path = Path(item.filename)
            if path.is_absolute() or '..' in path.parts or stat.S_ISLNK(item.external_attr >> 16) or item.filename in names or item.filename == 'RESTORE_INCOMPLETE':
                raise ValueError('Unsafe archive member')
            if not (destination / path).resolve().is_relative_to(destination):
                raise ValueError('Escaping archive path')
            names.add(item.filename)
        if 'history.sqlite3' not in names:
            raise ValueError('Database missing from backup')
        destination.mkdir(parents=True)
        marker = destination / 'RESTORE_INCOMPLETE'
        marker.write_text('Do not start the backend until restoration succeeds.')
        for item in archive.infolist():
            output = destination / item.filename
            if item.is_dir(): output.mkdir(parents=True, exist_ok=True); continue
            output.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(item) as src, output.open('xb') as dst:
                shutil.copyfileobj(src, dst)
    connection = sqlite3.connect(destination / 'history.sqlite3')
    try:
        if connection.execute('PRAGMA integrity_check').fetchone()[0] != 'ok':
            raise ValueError('Restored database failed integrity check')
        if connection.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Restored database has invalid foreign keys')
    finally:
        connection.close()
    marker.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['backup', 'restore'])
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    (backup if args.action == 'backup' else restore)(args.source, args.destination)
    print('Completed. Keep backups private: they contain submissions, session hashes, and hidden tests.')
