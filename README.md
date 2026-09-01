# BFSI Agents — Fraud Detection Lab (Clerivon AI)

**Repository:** [dataaispark-spec/bfsi-agents-fraud-lab](https://github.com/dataaispark-spec/bfsi-agents-fraud-lab)  
**Version:** 1.1.2 · **Scope:** Lab / pilot (synthetic tools)

Multi-agent **BFSI** use case: *demo* transaction fraud screening with a closed-loop analyst flywheel.

```
Monitor → Investigator → Adjudicator → Explainer → Feedback
         (synthetic MCP-style tools)              ↑
                 Case review (human) ─────────────┘
```

> **Not** a live core-banking integration.

Sister project: [hermes-skandashield-bots](https://github.com/dataaispark-spec/hermes-skandashield-bots).

---

## Quick start (demo)

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python scripts/demo_check.py   # must say READY FOR DEMO
python seed.py                 # optional cases in queue
streamlit run app.py           # http://localhost:8501
```

**Presenter script:** [DEMO.md](DEMO.md)  
**Full setup:** [SETUP_LAB.md](SETUP_LAB.md)

```bash
pytest tests/unit -v   # 16 tests
```

**Docker**

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
```

---

## Agent roles

| Agent | Role |
|-------|------|
| Monitor | Fast anomaly / threshold flag |
| Investigator | Synthetic tools (geo, device, merchant, sanctions, …) |
| Adjudicator | BLOCK / REVIEW / APPROVE |
| Explainer | Analyst-readable case file |
| Feedback | Flywheel from human confirm/override |

---

## Docs

| Doc | Purpose |
|-----|---------|
| [DEMO.md](DEMO.md) | Live demo playbook |
| [SETUP_LAB.md](SETUP_LAB.md) | Install & deploy |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Pipeline narrative |
| [HARNESS_ENGINEERING.md](HARNESS_ENGINEERING.md) | Guardrails / memory / verify / observe |
| [CHANGELOG.md](CHANGELOG.md) | Versions |

---

## License

Apache-2.0 — see [LICENSE](LICENSE).
