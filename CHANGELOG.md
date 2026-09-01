# Changelog

## [1.2.0] — 2026-09-01

### Cleanup (main)

- Removed obsolete artifacts: `.bundle` / `.zip`, nested `clerivon-fraud-detection-mas/`, committed `fraud_cases.db`, `generate_zip.py`
- Removed unused modules: `database_prod.py`, `auth.py`, `data_pipeline.py`, `prime_agents.py`
- Removed outdated docs: `DEPLOYMENT.md`, `VALIDATION_REPORT.md`, `ROADMAP.md`, `QUICKSTART_CLOUD.md`, `PUSH_INSTRUCTIONS.md`, `REPO_METADATA.md`
- Removed non-lab tests: `tests/cloud/*`, `tests/e2e/*`
- Slimmed `requirements.txt` to Streamlit + pydantic + dotenv (+ optional Postgres/MCP)
- Clear, single-path **README**

## [1.1.2] — 2026-09-01

- `scripts/demo_check.py`, `DEMO.md`, harness unit tests (16), pytest.ini

## [1.1.1] — 2026-09-01

- Repo rename to `bfsi-agents-fraud-lab`

## [1.1.0] — 2026-09-01

- Lab deploy: db factory, Docker lab overlay, entrypoint

## [1.0.0] — prior

- Initial multi-agent demo
