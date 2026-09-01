# BFSI Agents Fraud Lab — image (v1.1.1)
# https://github.com/dataaispark-spec/bfsi-agents-fraud-lab
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    APP_VERSION=1.1.1 \
    DB_BACKEND=sqlite \
    FRAUD_DB_PATH=/data/fraud_cases.db \
    AUTO_SEED=true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    postgresql-client \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fraud_agents/ ./fraud_agents/
COPY app.py seed.py ./
COPY scripts/ ./scripts/

RUN mkdir -p /data && chmod +x /app/scripts/entrypoint.sh

RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app /data
USER appuser

EXPOSE 8501 8765

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=5 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["bash", "/app/scripts/entrypoint.sh"]
