# Clerivon AI — BFSI Fraud Detection (Lab / Pilot)

**Version 1.1.0** · Multi-agent fraud **demo** with harness patterns  
**Repository:** [dataaispark-spec/agents-usecase](https://github.com/dataaispark-spec/agents-usecase)

> **Scope:** Synthetic end-to-end use case for lab and pilot demos.  
> Tools return mock data. Not a live core-banking integration.

---

## What you get

| Capability | Lab status |
|------------|------------|
| 5-agent pipeline (Monitor → Investigator → Adjudicator → Explainer → Feedback) | ✅ Synthetic |
| Streamlit UI (Live Feed, Case Review, Flywheel) | ✅ |
| SQLite persistence (default) | ✅ |
| Optional Postgres (lab-aligned schema) | ✅ |
| Docker lab deploy | ✅ |
| Harness engines (guardrails / memory / verify / observe) | ✅ Code present |
| Live bank / device / sanctions feeds | ❌ Mock only |
| Production SSO as default | ❌ Stubs |

Architecture inspiration: Hermes / Prime Agents-style **Agent = Model + Harness**.

Related cyber path kit (same org): [hermes-skandashield-bots](https://github.com/dataaispark-spec/hermes-skandashield-bots).

---

## Quick start (local)

```bash
git clone https://github.com/dataaispark-spec/agents-usecase.git
cd agents-usecase
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
streamlit run app.py
# http://localhost:8501
```

**E2E path:** Live Feed → `impossible_travel` → Generate → Case Review → Confirm/Override → Flywheel.

```bash
pytest tests/unit -v
```

Full lab options: **[SETUP_LAB.md](SETUP_LAB.md)**

---

## Docker lab (recommended pilot)

```bash
cp .env.example .env
# leave DB_BACKEND=sqlite for simplest run
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
# UI: http://localhost:8501
```

SQLite data lives in volume `clerivon_sqlite_data`.

Postgres mode:

```bash
# .env → DB_BACKEND=postgres
docker compose -f docker-compose.yml -f docker-compose.lab.yml --profile postgres up --build -d
```

---

## Architecture (lab)

```
Synthetic txn → Monitor → Investigator (mock tools)
                      → Adjudicator → Explainer → Case DB
Human review → Feedback / Flywheel metrics
```

| Layer | Tech |
|-------|------|
| UI | Streamlit |
| Agents | `fraud_agents/agents.py`, `prime_agents.py` |
| Tools | `fraud_agents/tools.py` (synthetic) |
| DB | SQLite default · Postgres optional via `db_factory` |
| Harness | `fraud_agents/harness.py` |
| MCP sample | `fraud_agents/mcp_server.py` |

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [SETUP_LAB.md](SETUP_LAB.md) | Deploy & test lab/pilot |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Agent flow narrative |
| [HARNESS_ENGINEERING.md](HARNESS_ENGINEERING.md) | Guardrails / memory / verify / observe |
| [CHANGELOG.md](CHANGELOG.md) | Version history |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Longer deploy notes (treat as aspirational where marked prod) |

---

## License

See [LICENSE](LICENSE). Confirm terms with the repository owner before commercial use.
