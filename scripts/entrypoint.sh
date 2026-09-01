#!/bin/bash
set -euo pipefail

echo "[clerivon] v${APP_VERSION:-1.1.0} starting (DB_BACKEND=${DB_BACKEND:-sqlite})"

if [ "${DB_BACKEND:-sqlite}" = "postgres" ] || [ "${DB_BACKEND:-}" = "postgresql" ]; then
  echo "[clerivon] waiting for postgres at ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
  for i in $(seq 1 30); do
    if pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-clerivon_user}" >/dev/null 2>&1; then
      echo "[clerivon] postgres is ready"
      break
    fi
    sleep 2
  done
fi

if [ "${AUTO_SEED:-true}" = "true" ]; then
  echo "[clerivon] seeding sample cases (idempotent best-effort)..."
  python seed.py || echo "[clerivon] seed skipped/failed (non-fatal for UI boot)"
fi

exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501
