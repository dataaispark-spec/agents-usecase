# BFSI Agents — Fraud Detection Lab (Clerivon AI)

**Repository:** [dataaispark-spec/bfsi-agents-fraud-lab](https://github.com/dataaispark-spec/bfsi-agents-fraud-lab)  
**Version:** 1.1.1 · **Scope:** Lab / pilot (synthetic tools)

Multi-agent **BFSI** use case: real-time *demo* transaction fraud screening with a closed-loop analyst flywheel.

```
Monitor → Investigator → Adjudicator → Explainer → Feedback
         (synthetic MCP-style tools)              ↑
                 Case review (human) ─────────────┘
```

> **Not** a live core-banking integration. Tools return mock profiles, geo-velocity, devices, and sanctions data.

Sister project (cyber attack paths): [hermes-skandashield-bots](https://github.com/dataaispark-spec/hermes-skandashield-bots).

---

## Topics

`bfsi` · `fraud-detection` · `multi-agent` · `agents` · `mcp` · `harness` · `lab-pilot` · `banking` · `synthetic-demo` · `python` · `docker`

*(Configured on the GitHub repo About panel.)*

---

## Quick start

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python seed.py
streamlit run app.py
# http://localhost:8501
```

**Docker lab**

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
# http://localhost:8501
```

Full steps: **[SETUP_LAB.md](SETUP_LAB.md)**

**E2E check:** Live Feed → `impossible_travel` → Generate → Case Review → Confirm/Override → Flywheel.

```bash
pytest tests/unit -v
```

---

## BFSI agent roles

| Agent | Role |
|-------|------|
| Monitor | Fast anomaly / threshold flag |
| Investigator | Synthetic tools (geo, device, merchant, sanctions, …) |
| Adjudicator | BLOCK / REVIEW / APPROVE |
| Explainer | Analyst-readable case file |
| Feedback | Flywheel from human confirm/override |

---

## Lab stack

| Layer | Tech |
|-------|------|
| UI | Streamlit |
| Agents | `fraud_agents/agents.py`, `prime_agents.py` |
| Tools | `fraud_agents/tools.py` (synthetic) |
| DB | SQLite default · Postgres optional (`db_factory`) |
| Harness | `fraud_agents/harness.py` |
| MCP sample | `fraud_agents/mcp_server.py` |
| Deploy | Docker Compose + `docker-compose.lab.yml` |

---

## Docs

| Doc | Purpose |
|-----|---------|
| [SETUP_LAB.md](SETUP_LAB.md) | Deploy & E2E test |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Pipeline walkthrough |
| [HARNESS_ENGINEERING.md](HARNESS_ENGINEERING.md) | Guardrails / memory / verify / observe |
| [CHANGELOG.md](CHANGELOG.md) | Versions |
| [REPO_METADATA.md](REPO_METADATA.md) | About text, topics, labels |

---

## License

Apache-2.0 — see [LICENSE](LICENSE).
