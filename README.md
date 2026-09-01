# BFSI Agents Fraud Lab

**Multi-agent fraud detection demo for banking / financial services (BFSI).**  
Lab / pilot only — synthetic tools, not a live core-banking integration.

| | |
|--|--|
| **Repo** | [dataaispark-spec/bfsi-agents-fraud-lab](https://github.com/dataaispark-spec/bfsi-agents-fraud-lab) |
| **Version** | 1.2.1 |
| **UI** | Streamlit |
| **Default DB** | SQLite |

```
Transaction (synthetic)
    → Monitor → Investigator → Adjudicator → Explainer
                                              ↓
                                         Case (DB)
                                              ↓
                              Human review → Feedback (flywheel)
```

---

## What this is

A **working lab** that shows how specialised agents can:

1. Flag risky transactions (Monitor)
2. Gather evidence via mock tools — geo-velocity, device, merchant, sanctions (Investigator)
3. Decide BLOCK / REVIEW / APPROVE (Adjudicator)
4. Write an analyst-readable case (Explainer)
5. Learn from human confirm/override (Feedback / Flywheel)

**Not included:** live bank APIs, production SSO, SOC2 evidence, real OFAC feeds.

---

## Quick start

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python scripts/demo_check.py       # READY FOR DEMO
python scripts/demo_emulator.py    # headless full DEMO path
python seed.py                     # optional sample cases
streamlit run app.py               # http://localhost:8501
```

**Tests**

```bash
pytest tests/unit -v
```

**Docker (optional)**

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
```

---

## Demo path (UI)

1. **Live Feed** → scenario `impossible_travel` → **Generate Transaction**
2. Walk agent expanders (Monitor → Investigator → Adjudicator → case saved)
3. **Case Review** → Confirm AI or Override
4. **Flywheel Analytics** → feedback metrics

Notes: **[DEMO.md](DEMO.md)** · Setup: **[SETUP_LAB.md](SETUP_LAB.md)**

---

## Repository layout

```
app.py                 Streamlit UI
seed.py                Sample cases
requirements.txt       Minimal deps
fraud_agents/
  agents.py            5-agent pipeline
  tools.py             Synthetic investigation tools
  database.py          SQLite
  database_lab_pg.py   Optional Postgres
  db_factory.py        DB_BACKEND=sqlite|postgres
  harness.py           Guardrails / memory / verify / observe
  mcp_server.py        Optional MCP sample
scripts/
  demo_check.py        Pre-demo smoke
  demo_emulator.py     Headless DEMO.md path
  entrypoint.sh        Docker entry
tests/unit/            Harness tests (16)
Dockerfile, docker-compose*.yml
```

---

## Dependencies

| Package | Role |
|---------|------|
| `streamlit` | UI |
| `pydantic` | Harness models |
| `python-dotenv` | Env |
| `pytest` | Tests |
| `psycopg2-binary` | Optional Postgres |
| `mcp` | Optional MCP server |

---

## License

Apache-2.0 — [LICENSE](LICENSE).
