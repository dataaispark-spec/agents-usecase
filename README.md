# BFSI Agents Fraud Lab

**Multi-agent fraud detection demo for banking / financial services (BFSI).**  
Lab / pilot only — synthetic tools, not a live core-banking integration.

| | |
|--|--|
| **Repo** | [dataaispark-spec/bfsi-agents-fraud-lab](https://github.com/dataaispark-spec/bfsi-agents-fraud-lab) |
| **Version** | 1.2.0 |
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

python scripts/demo_check.py       # expect: READY FOR DEMO
python seed.py                     # optional sample cases
streamlit run app.py               # http://localhost:8501
```

**Tests**

```bash
pytest tests/unit -v               # harness unit tests
```

**Docker (optional)**

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
# UI: http://localhost:8501
```

---

## Demo path (UI)

1. **Live Feed** → scenario `impossible_travel` → **Generate Transaction**
2. Walk agent expanders (Monitor → Investigator → Adjudicator → case saved)
3. **Case Review** → Confirm AI or Override
4. **Flywheel Analytics** → see feedback metrics

Full presenter notes: **[DEMO.md](DEMO.md)**  
Setup detail: **[SETUP_LAB.md](SETUP_LAB.md)**

---

## Repository layout (kept)

```
app.py                 # Streamlit UI
seed.py                # Sample cases
requirements.txt       # Minimal deps
fraud_agents/
  agents.py            # 5-agent pipeline
  tools.py             # Synthetic investigation tools
  database.py          # SQLite
  database_lab_pg.py   # Optional Postgres adapter
  db_factory.py        # DB_BACKEND=sqlite|postgres
  harness.py           # Guardrails / memory / verify / observe
  mcp_server.py        # Optional MCP tool server sample
scripts/
  demo_check.py        # Pre-demo smoke test
  entrypoint.sh        # Docker entry
tests/unit/            # Harness tests
Dockerfile
docker-compose.yml
docker-compose.lab.yml
DEMO.md  SETUP_LAB.md  CHANGELOG.md
```

---

## Dependencies (required)

| Package | Why |
|---------|-----|
| `streamlit` | UI |
| `pydantic` | Harness models |
| `python-dotenv` | Env config |
| `pytest` | Tests |

| Optional | Why |
|----------|-----|
| `psycopg2-binary` | `DB_BACKEND=postgres` |
| `mcp` | Sample MCP server only |

---

## Configuration

| Variable | Default | Meaning |
|----------|---------|---------|
| `DB_BACKEND` | `sqlite` | `sqlite` or `postgres` |
| `FRAUD_DB_PATH` | `fraud_cases.db` | SQLite file |
| `AUTO_SEED` | `true` (Docker) | Seed on container start |

See `.env.example`.

---

## License

Apache-2.0 — see [LICENSE](LICENSE).
