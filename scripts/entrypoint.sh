#!/bin/bash
set -euo pipefail

echo "[bfsi-agents-fraud-lab] v${APP_VERSION:-1.1.1} starting (DB_BACKEND=${DB_BACKEND:-sqlite})"

if [ "${DB_BACKEND:-sqlite}" = "postgres" ] || [ "${DB_BACKEND:-}" = "postgresql" ]; then
  echo "[bfsi-agents-fraud-lab] waiting for postgres at ${DB_HOST:-postgres}:${DB_PORT:-5432}..."
  for i in $(seq 1 30); do
    if pg_isready -h "${DB_HOST:-postgres}" -p "${DB_PORT:-5432}" -U "${DB_USER:-clerivon_user}" >/dev/null 2>&1; then
      echo "[bfsi-agents-fraud-lab] postgres is ready"
      break
    fi
    sleep 2
  done
fi

if [ "${AUTO_SEED:-true}" = "true" ]; then
  echo "[bfsi-agents-fraud-lab] seeding sample cases (best-effort)..."
  python seed.py || echo "[bfsi-agents-fraud-lab] seed skipped/failed (non-fatal for UI boot)"
fi

exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501
