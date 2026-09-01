# Architecture (lab)

## Pipeline

```
Synthetic transaction
  → MonitorAgent          # threshold / anomaly flags
  → InvestigatorAgent     # tools.py (mock geo, device, merchant, sanctions, …)
  → AdjudicatorAgent      # BLOCK | REVIEW | APPROVE
  → ExplainerAgent        # case file JSON
  → SQLite / Postgres     # cases + agent_responses
  → Human (Streamlit)     # confirm / override
  → FeedbackAgent         # flywheel metrics
```

## Harness (`fraud_agents/harness.py`)

Optional wrapper pattern: **Agent = Model + Harness**

| Engine | Role |
|--------|------|
| Guardrails | PII redact, injection block |
| Memory | Short-term window + mock long-term search |
| Verification | BLOCK requires evidence |
| Observability | Span lifecycle |

The live Streamlit path uses `agents.py` + `tools.py` directly; harness is unit-tested and available for extension.

## Data

| Backend | Module |
|---------|--------|
| SQLite (default) | `database.py` |
| Postgres (optional) | `database_lab_pg.py` via `db_factory.py` |

Tools return **synthetic** profiles only.
