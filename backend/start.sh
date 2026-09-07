#!/usr/bin/env bash
set -e

echo "==> EcoFinwize API: running database migrations"
alembic upgrade head

echo "==> EcoFinwize API: starting server on port ${PORT:-8100}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8100}"