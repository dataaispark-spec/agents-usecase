# BFSI Agents — Fraud Detection Lab (Clerivon AI)

**Repo name (recommended):** `bfsi-agents-fraud-lab`  
**Current GitHub path:** [dataaispark-spec/agents-usecase](https://github.com/dataaispark-spec/agents-usecase) *(rename when ready — see [REPO_METADATA.md](REPO_METADATA.md))*  
**Version:** 1.1.0 · **Scope:** Lab / pilot (synthetic tools)

Multi-agent **BFSI** use case: real-time *demo* transaction fraud screening with a closed-loop analyst flywheel.

```
Monitor → Investigator → Adjudicator → Explainer → Feedback
         (synthetic MCP-style tools)              ↑
                 Case review (human) ─────────────┘
```

> **Not** a live core-banking integration. Tools return mock profiles, geo-velocity, devices, and sanctions data.

Sister project (cyber attack paths): [hermes-skandashield-bots](https://github.com/dataaispark-spec/hermes-skandashield-bots).

---

## Tags / topics

`bfsi` · `fraud-detection` · `multi-agent` · `ai-agents` · `streamlit` · `mcp` · `harness` · `lab-pilot` · `python` · `docker`

---

## Quick start

```bash
git clone https://github.com/dataaispark-spec/agents-usecase.git
cd agents-usecase
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python seed.py
streamlit run app.py
# http://localhost:8501
```

**Docker lab**

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
```

Full steps: **[SETUP_LAB.md](SETUP_LAB.md)** · Metadata / rename: **[REPO_METADATA.md](REPO_METADATA.md)**

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

## Docs

| Doc | Purpose |
|-----|---------|
| [SETUP_LAB.md](SETUP_LAB.md) | Deploy & E2E test |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Pipeline walkthrough |
| [HARNESS_ENGINEERING.md](HARNESS_ENGINEERING.md) | Guardrails / memory / verify / observe |
| [CHANGELOG.md](CHANGELOG.md) | Versions |
| [REPO_METADATA.md](REPO_METADATA.md) | Rename, About text, topics, labels |

---

## License

See [LICENSE](LICENSE). Confirm terms before commercial use.
