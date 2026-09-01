# Repository metadata (About, topics, rename)

## Recommended GitHub name

**`bfsi-agents-fraud-lab`**

- **BFSI** — banking / financial services / insurance domain  
- **agents** — multi-agent system  
- **fraud-lab** — fraud detection lab/pilot (honest scope)

Canonical URL after rename:  
https://github.com/dataaispark-spec/bfsi-agents-fraud-lab  

GitHub keeps redirects from `agents-usecase` → new name for clones and links.

## About (paste into GitHub → Settings → General → Description)

```
Clerivon AI lab/pilot: multi-agent BFSI fraud detection (Monitor→Investigator→Adjudicator→Explainer→Feedback). Synthetic E2E demo — Streamlit, harness, SQLite/Postgres, Docker.
```

## Website (optional)

```
https://github.com/dataaispark-spec/bfsi-agents-fraud-lab
```

## Topics / tags (Settings → General → Topics)

```
bfsi
fraud-detection
multi-agent
ai-agents
streamlit
mcp
harness
lab-pilot
python
banking
docker
synthetic-demo
clerivon
```

## Issue labels (already created on this repo)

| Label | Color | Use |
|-------|-------|-----|
| `bfsi` | green | Domain |
| `fraud-detection` | red | Feature area |
| `multi-agent` | purple | Agent pipeline |
| `lab-pilot` | yellow | Scope / not prod cutover |
| `docker` | blue | Deploy |
| `harness` | blue | Guardrails etc. |
| `mcp` | light blue | MCP tools |
| `documentation` | blue | Docs |

## Rename steps (owner UI or CLI)

**UI:** Repo → **Settings** → **General** → Repository name → `bfsi-agents-fraud-lab` → Rename  

**CLI (with `gh` authenticated as owner):**

```bash
gh repo rename bfsi-agents-fraud-lab --repo dataaispark-spec/agents-usecase
gh repo edit dataaispark-spec/bfsi-agents-fraud-lab \
  --description "Clerivon AI lab/pilot: multi-agent BFSI fraud detection (Monitor→Investigator→Adjudicator→Explainer→Feedback). Synthetic E2E demo — Streamlit, harness, SQLite/Postgres, Docker." \
  --add-topic bfsi --add-topic fraud-detection --add-topic multi-agent \
  --add-topic ai-agents --add-topic streamlit --add-topic mcp \
  --add-topic harness --add-topic lab-pilot --add-topic python \
  --add-topic banking --add-topic docker --add-topic synthetic-demo \
  --add-topic clerivon
```

> The GitHub connector used for code pushes does not expose **rename repository** or **set topics** APIs; those two steps need owner UI or `gh` as above.
