# Changelog

## [1.1.2] — 2026-09-01

### Demo readiness

- `scripts/demo_check.py` — one-shot pipeline + harness + DB smoke test
- `DEMO.md` — presenter playbook and checklist
- Unit tests aligned with harness API (16/16)
- `pytest.ini` with `pythonpath = .`
- `.gitignore` for venv, `__pycache__`, local `.db`
- Harness: use `model_dump()` instead of deprecated `.dict()`

## [1.1.1] — 2026-09-01

### Rename alignment

- Canonical repo: **dataaispark-spec/bfsi-agents-fraud-lab**
- README, SETUP_LAB, REPO_METADATA clone/paths updated

## [1.1.0] — 2026-09-01

### Lab / pilot deployability

- DB factory (`sqlite` / `postgres`)
- Lab Postgres adapter, Docker lab overlay, entrypoint + auto-seed
- Honest lab scope in UI Settings

### Not claimed in 1.1.x

- Live core-banking / OFAC / device APIs
- Production SSO as default UI gate
- SOC2 / bank TPS as verified CI metrics

## [1.0.0] — prior

- Initial multi-agent demo, harness, Streamlit UI, docs
