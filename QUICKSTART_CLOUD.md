# ☁️ QuickStart: Cloud-Native Deployment (Free Tier)

> **Executive Summary**: Migrate your local Docker Compose pilot to a global, serverless production environment using **100% Free Tier** services. 
> **Zero Infrastructure Management. Zero Cost.**

## 🚀 The "One-Click" Migration Architecture

| Local Component | ☁️ Cloud Alternative (Free) | Benefit |
| :--- | :--- | :--- |
| **PostgreSQL + pgvector** | **Supabase** or **Neon** | Auto-scaling, Branching, REST API |
| **Streamlit App** | **Streamlit Community Cloud** | Global CDN, No Cold Starts |
| **MCP Tool Server** | **Google Cloud Run** | Scale-to-Zero, 2M req/mo free |

---

## 📋 Step-by-Step Migration (15 Minutes)

### Step 1: Database (Supabase/Neon)
1. Create a free project at [supabase.com](https://supabase.com) or [neon.tech](https://neon.tech).
2. Enable `pgvector` extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy your **Connection String** (looks like `postgresql://postgres:...`).

### Step 2: MCP Tools (Google Cloud Run)
1. Containerize the MCP server (already in `Dockerfile`).
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy clerivon-mcp --source . --platform managed --allow-unauthenticated
   ```
3. Copy the **Service URL** (e.g., `https://clerivon-mcp-xyz.run.app`).

### Step 3: Frontend (Streamlit Cloud)
1. Push your code to **GitHub**.
2. Connect repo at [share.streamlit.io](https://share.streamlit.io).
3. Set **Secrets** (`.streamlit/secrets.toml`) in dashboard:
   ```toml
   [database]
   url = "YOUR_SUPABASE_CONNECTION_STRING"
   
   [mcp]
   endpoint = "YOUR_CLOUD_RUN_URL"
   ```
4. Click **Deploy**.

---

## ✅ Validation Checklist

Run this locally to verify your cloud setup before going live:

```bash
python -c "
import os
from fraud_agents.database_prod import ProductionDatabase
from fraud_agents.mcp_client import MCPClient

# Test DB
db = ProductionDatabase(os.getenv('DATABASE_URL'))
print('✅ Database Connected:', db.health_check())

# Test MCP
mcp = MCPClient(os.getenv('MCP_ENDPOINT'))
print('✅ MCP Server Reachable:', mcp.health_check())
"
```

## 💰 Cost Breakdown

| Service | Free Limit | Estimated Monthly Cost |
| :--- | :--- | :--- |
| **Neon/Supabase** | 500MB - 1GB | $0 |
| **Streamlit Cloud** | 1GB RAM / App | $0 |
| **Cloud Run** | 2M Requests | $0 |
| **Total** | | **$0.00** |

> **Note**: Once traffic exceeds free tiers, estimated cost is ~$15-25/month for moderate usage.

## 🔄 Hybrid Strategy

| Phase | Architecture | Use Case |
| :--- | :--- | :--- |
| **Pilot** | Local Docker Compose | Internal Dev, Air-gapped Demo |
| **Demo** | Cloud Free Tier | Client Presentations, PoC |
| **Production** | Cloud Paid / Private VPC | Live Enterprise Traffic |

---

**Next Steps**: For detailed configuration, security hardening, and CI/CD pipelines, refer to `DEPLOYMENT.md`.
