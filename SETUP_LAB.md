# Setup — BFSI Agents Fraud Lab

## Local

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/demo_check.py
python seed.py
streamlit run app.py
```

## Docker

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
```

SQLite data: volume `clerivon_sqlite_data`.

Postgres (optional):

```bash
# .env → DB_BACKEND=postgres
docker compose -f docker-compose.yml -f docker-compose.lab.yml --profile postgres up --build -d
```

## Env

| Variable | Default |
|----------|---------|
| `DB_BACKEND` | `sqlite` |
| `FRAUD_DB_PATH` | `fraud_cases.db` |
| `AUTO_SEED` | `true` (containers) |

## Scope

Works: synthetic 5-agent pipeline, SQLite/Postgres lab DB, Streamlit UI, unit tests.  
Does not: live bank feeds, production SSO.
