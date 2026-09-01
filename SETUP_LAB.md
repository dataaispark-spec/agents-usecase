# BFSI Agents Fraud Lab v1.1.1 — Setup

Honest scope: **synthetic multi-agent fraud demo** with optional Docker.  
Not a live core-banking integration.

**Repo:** https://github.com/dataaispark-spec/bfsi-agents-fraud-lab

## Option A — Local (fastest)

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python seed.py
streamlit run app.py
# http://localhost:8501
```

**E2E test path**

1. **Live Feed** → scenario `impossible_travel` → Generate  
2. Confirm case appears  
3. **Case Review** → Confirm or Override  
4. **Flywheel Analytics** → feedback listed  

```bash
pytest tests/unit -v
```

## Option B — Docker lab (SQLite volume — recommended pilot)

```bash
cp .env.example .env
# set SECRET_KEY; leave DB_BACKEND=sqlite for simplest pilot

docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
open http://localhost:8501
```

Data persists in Docker volume `clerivon_sqlite_data`.

## Option C — Docker + Postgres

```bash
# in .env
DB_BACKEND=postgres
DB_PASSWORD=choose-a-strong-password

docker compose -f docker-compose.yml -f docker-compose.lab.yml --profile postgres up --build -d
```

App waits for Postgres, creates lab-aligned tables, optional seed.

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `DB_BACKEND` | `sqlite` | `sqlite` or `postgres` |
| `FRAUD_DB_PATH` | `fraud_cases.db` | SQLite file path |
| `DB_HOST` / `DB_PORT` / `DB_NAME` / `DB_USER` / `DB_PASSWORD` | see compose | Postgres |
| `AUTO_SEED` | `true` | Run `seed.py` on container start |
| `LLM_PROVIDER` | `off` in lab | Tools are synthetic; LLM optional |

## What works vs not

| Works in lab | Not included |
|--------------|--------------|
| 5-agent pipeline on synthetic txns | Live bank / device / OFAC feeds |
| Case review + flywheel feedback | Real SSO (code stubs only) |
| SQLite or lab Postgres | Full production HA / SOC2 evidence |
| Unit tests for harness | Load test at bank TPS |

## Troubleshoot

```bash
docker compose logs -f app
docker compose exec app python -c "from fraud_agents.db_factory import db; print(db().get_flywheel_metrics())"
```
