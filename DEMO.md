# Demo playbook — BFSI Agents Fraud Lab

**Repo:** https://github.com/dataaispark-spec/bfsi-agents-fraud-lab  
**Version:** 1.1.2 · Lab / pilot (synthetic data)

## 5-minute setup

```bash
git clone https://github.com/dataaispark-spec/bfsi-agents-fraud-lab.git
cd bfsi-agents-fraud-lab
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# automated readiness
python scripts/demo_check.py

# optional seed for Case Review queue
python seed.py

streamlit run app.py
# open http://localhost:8501
```

Docker alternative:

```bash
cp .env.example .env
docker compose -f docker-compose.yml -f docker-compose.lab.yml up --build -d
```

## Live demo script (≈8 minutes)

### 1. Framing (30s)

> Five specialised agents screen a transaction: Monitor → Investigator → Adjudicator → Explainer → Feedback.  
> Tools are **synthetic** for the lab — same shape as production MCP integrations.

### 2. Live Feed — impossible travel (2 min)

1. Open **Live Feed**
2. Scenario: **`impossible_travel`**
3. Click **Generate Transaction**
4. Walk the expanders: Monitor → Investigator (geo-velocity) → Adjudicator → case saved

**Talk track:** London → Singapore in ~20 minutes → impossible travel flag → elevated risk.

### 3. Contrast — normal grocery (1 min)

1. Scenario: **`normal_transaction`**
2. Generate — expect auto-approve or low risk path

### 4. Case Review + human-in-the-loop (2 min)

1. **Case Review** — open a pending case
2. **Confirm AI** or **Override**
3. Explain: feedback is stored for the flywheel

### 5. Flywheel (1 min)

1. **Flywheel Analytics** — totals, agreement, recent feedback
2. Message: closed loop — analysts train thresholds over time

### 6. Settings honesty (30s)

Show **Settings**: lab mode, synthetic tools, version string.

## Pre-demo checklist

```bash
python scripts/demo_check.py   # must print READY FOR DEMO
pytest tests/unit -v           # 16 passed
```

| Check | Pass? |
|-------|-------|
| Port 8501 free | |
| Browser zoom readable | |
| Seed ran (cases in queue) | |
| No live bank credentials needed | ✅ |

## What not to claim

- Live core-banking / OFAC connectivity  
- Production SSO  
- Bank TPS / SOC2 as measured in this lab  
