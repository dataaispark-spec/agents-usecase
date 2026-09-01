# Changelog

## [1.1.0] — 2026-09-01

### Lab / pilot deployability

- **DB factory** (`fraud_agents/db_factory.py`): `DB_BACKEND=sqlite|postgres`
- **Lab Postgres adapter** aligned with SQLite case/feedback schema used by the UI
- **Docker lab overlay** `docker-compose.lab.yml` with SQLite volume + optional Postgres profile
- **Entrypoint** `scripts/entrypoint.sh`: wait for Postgres (when needed), optional auto-seed, Streamlit
- **Dockerfile** Python 3.12, `/data` volume path, entrypoint default
- **app.py / seed.py** use db factory; Settings page honest about lab scope
- **SETUP_LAB.md** step-by-step local + Docker
- **README** clone URL fixed to `dataaispark-spec/agents-usecase`; production claims tempered

### Not claimed in 1.1.0

- Live core-banking / OFAC / device APIs (still synthetic mocks)
- Production SSO as default UI gate
- SOC2 / bank TPS benchmarks as verified CI metrics

## [1.0.0] — prior

- Initial multi-agent demo, harness, Streamlit UI, docs
