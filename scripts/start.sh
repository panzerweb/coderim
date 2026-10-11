#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -f .venv/bin/python ] || [ ! -f frontend/dist/index.html ]; then
  echo 'Install dependencies and build the frontend first; see README.md.' >&2
  exit 1
fi
exec .venv/bin/python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
