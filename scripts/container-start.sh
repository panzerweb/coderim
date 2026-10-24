#!/bin/sh
set -eu
# Render mounts the persistent disk after the image is built. Give the service
# user ownership of this data directory before dropping root privileges.
if [ "$(id -u)" = 0 ]; then
    runtime_path="$(realpath -m "${RELAY_RUNTIME:-/var/data/relay}")"
    case "$runtime_path" in
        /var/data/*) ;;
        *) echo 'Container runtime must be a directory beneath /var/data' >&2; exit 1 ;;
    esac
    mkdir -p "$runtime_path"
    chown -h -R relay:relay "$runtime_path"
    exec gosu relay "$0" "$@"
fi
if [ "$#" -eq 0 ]; then
    set -- python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port "${PORT:-8000}" --workers 1
fi
exec "$@"
