# Clerivon AI Fraud Detection - Production Deployment Guide

## 🚀 Quick Start: Deploy to Production

### Prerequisites
- Docker & Docker Compose installed
- PostgreSQL 16+ with pgvector extension (or use provided container)
- Docker Hub account for image publishing
- LLM API keys (OpenAI/Anthropic) or run in deterministic mode

---

## ✅ Phase 1: MCP Server Endpoints

**Status:** ✅ Complete  
**File:** `fraud_agents/mcp_server.py`

The fraud detection tools have been converted to standard MCP server endpoints:

```bash
# Run MCP Server locally
python -m fraud_agents.mcp_server

# Test MCP tools
npx @modelcontextprotocol/inspector python -m fraud_agents.mcp_server
```

**Available MCP Tools:**
- `get_customer_profile` - Customer risk profiling
- `get_device_history` - Device reputation checks
- `calculate_geo_velocity` - Impossible travel detection
- `check_merchant_risk` - MCC code risk scoring
- `get_recent_transactions` - Transaction history
- `check_sanctions_list` - OFAC/UN sanctions screening
- `submit_case_decision` - Human feedback loop

---

## ✅ Phase 2: PostgreSQL + pgvector Database

**Status:** ✅ Complete  
**Files:** `fraud_agents/database_prod.py`, `init-db.sql`, `docker-compose.yml`

Replace SQLite with enterprise-grade PostgreSQL:

```bash
# Start PostgreSQL with pgvector
docker-compose up -d postgres

# Verify connection
psql -h localhost -U clerivon_user -d clerivon_fraud

# Run semantic search example
SELECT tx_id, customer_id, amount, 
       1 - (embedding <=> '[0.1,0.2...]'::vector) as similarity
FROM transactions
ORDER BY embedding <=> '[0.1,0.2...]'::vector
LIMIT 5;
```

**Features:**
- Vector embeddings for semantic transaction search
- JSONB columns for flexible evidence storage
- Audit logging for compliance (SOX, GDPR, PCI-DSS)
- Automatic indexing for performance

---

## ✅ Phase 3: Enterprise SSO/RBAC Authentication

**Status:** ✅ Complete  
**File:** `fraud_agents/auth.py`

Integrated SSO with role-based access control:

### Supported Providers:
- **Azure AD** (Microsoft Entra ID)
- **Okta**
- **Keycloak** (self-hosted)

### Role Hierarchy:
| Role | Level | Permissions |
|------|-------|-------------|
| ANALYST | 1 | View cases, submit recommendations |
| SENIOR_ANALYST | 2 | + Approve/escalate cases |
| MANAGER | 3 | + Block transactions, export reports |
| ADMIN | 4 | Full system access |

### Configuration:
```bash
# Copy environment template
cp .env.example .env

# Edit with your SSO credentials
vim .env
```

---

## ✅ Phase 4: Containerized Deployment

**Status:** ✅ Complete  
**Files:** `Dockerfile`, `docker-compose.yml`, `.github/workflows/ci-cd.yml`

### Option A: Local Docker Deployment

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Access application
# Streamlit UI: http://localhost:8501
# PostgreSQL: localhost:5432
# MCP Server: localhost:8765
```

### Option B: Docker Hub Distribution

```bash
# Set secrets in GitHub repository:
# - DOCKER_HUB_USERNAME
# - DOCKER_HUB_ACCESS_TOKEN

# CI/CD will automatically build and push on main branch commit
# Image available at: docker.io/<username>/clerivon-fraud-detection:latest

# Deploy from Docker Hub
docker pull <username>/clerivon-fraud-detection:latest
docker run -p 8501:8501 --env-file .env <username>/clerivon-fraud-detection:latest
```

### Option C: Air-Gapped/Sovereign Cloud Deployment

For banks requiring air-gapped environments:

```bash
# 1. Build image on connected machine
docker build -t clerivon-fraud:latest .

# 2. Save image to tarball
docker save -o clerivon-fraud.tar clerivon-fraud:latest
docker save -o pgvector-pg16.tar pgvector/pgvector:pg16

# 3. Transfer to air-gapped environment via secure media
scp clerivon-fraud.tar pgvector-pg16.tar secure-server:/deploy/

# 4. Load images on air-gapped server
docker load -i clerivon-fraud.tar
docker load -i pgvector-pg16.tar

# 5. Deploy offline
docker-compose up -d
```

---

## 🔧 Validation Checklist

Run these commands to verify successful deployment:

```bash
# 1. Check all containers are running
docker-compose ps
# Expected: All services show "Up" status

# 2. Test database connection
docker-compose exec postgres psql -U clerivon_user -d clerivon_fraud -c "SELECT version();"
# Expected: PostgreSQL 16.x with vector extension

# 3. Verify pgvector extension
docker-compose exec postgres psql -U clerivon_user -d clerivon_fraud -c "\dx"
# Expected: vector extension listed

# 4. Test Streamlit health endpoint
curl http://localhost:8501/_stcore/health
# Expected: {"status": "ok"}

# 5. Test MCP server (if running separately)
python -c "from fraud_agents.mcp_server import mcp; print('MCP Server OK')"
# Expected: MCP Server OK

# 6. Check audit logging
docker-compose exec postgres psql -U clerivon_user -d clerivon_fraud -c "SELECT COUNT(*) FROM audit_log;"
# Expected: At least 1 entry (database init)
```

---

## 📊 Monitoring & Observability

### Prometheus Metrics
```bash
# Access metrics endpoint
curl http://localhost:9090/metrics
```

### Key Metrics Tracked:
- Transaction processing latency
- Agent execution time
- False positive rate
- Flywheel threshold adjustments
- Database query performance

---

## 🔐 Security Hardening Checklist

Before production deployment:

- [ ] Change all default passwords in `.env`
- [ ] Generate strong `SECRET_KEY` (32+ random characters)
- [ ] Configure SSO with corporate identity provider
- [ ] Enable TLS/SSL for all endpoints
- [ ] Restrict network access to trusted IPs
- [ ] Enable audit logging for all actions
- [ ] Set up automated backups for PostgreSQL
- [ ] Configure log rotation and retention policies
- [ ] Run security scan: `docker scout cve <image>`

---

## 🎯 Next Steps After Deployment

1. **Seed Initial Data**: Run `python seed.py` to populate test cases
2. **Configure LLM**: Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` in `.env`
3. **Customize Tools**: Modify `mcp_server.py` to connect to client's core banking systems
4. **Train Analysts**: Walk through the 7-minute demo script
5. **Monitor Flywheel**: Watch false positive rates decrease over time

---

## 📞 Support

For enterprise support and custom integrations:
- Documentation: `/workspace/README.md`
- MCP Specification: https://modelcontextprotocol.io
- pgvector Docs: https://github.com/pgvector/pgvector

---

## ☁️ OPTIONAL: Cloud-Native Migration (Free Tier Serverless)

**Status:** ✅ Complete  
**Purpose:** Migrate from local Docker Compose to distributed cloud serverless architecture for production scaling while maintaining zero-cost operations.

This section provides **additive deployment options** that complement the existing Docker Compose workflow. Use these free-tier cloud services to scale pilots into production without infrastructure management overhead.

### Migration Architecture Matrix

```
┌─────────────────────────────────────┐         ┌─────────────────────────────────────┐
│   LOCAL DOCKER COMPOSE (Pilot)      │         │   CLOUD SERVERLESS (Production)     │
├─────────────────────────────────────┤         ├─────────────────────────────────────┤
│  app: Streamlit + Agents            │  ───>>  │  Streamlit Cloud / HF Spaces        │
│  mcp: Tool Servers (stdio)          │  ───>>  │  Google Cloud Run / Smithery.ai     │
│  postgres: DB + pgvector (local)    │  ───>>  │  Supabase / Neon / Aiven DB         │
└─────────────────────────────────────┘         └─────────────────────────────────────┘
```

---

### Step 1: Database Layer Migration (PostgreSQL + pgvector)

Replace local PostgreSQL container with managed serverless database:

#### Option A: Supabase (Recommended for Full Backend)
**Free Tier:** 500 MB storage, 1 GB file storage, 2 active projects

**Benefits:**
- Auto-generates REST API on top of Postgres tables
- Built-in authentication & real-time listeners
- Native pgvector support

**Setup Steps:**
1. Create account at https://supabase.com
2. New Project → Choose region → Set database password
3. SQL Editor → Run: `CREATE EXTENSION IF NOT EXISTS vector;`
4. Get connection string from Settings → Database
5. Update `.env`:
   ```bash
   DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres
   ```

#### Option B: Neon (Best for Dev/Prod Branching)
**Free Tier:** 512 MB storage, 100 compute unit hours/month

**Benefits:**
- Serverless auto-scale to zero
- Database branching (Git-like workflows)
- Instant provisioning

**Setup Steps:**
1. Create account at https://neon.tech
2. New Project → Auto-provisions primary branch
3. SQL Editor → Run: `CREATE EXTENSION IF NOT EXISTS vector;`
4. Copy connection string from Dashboard
5. Update `.env`:
   ```bash
   DATABASE_URL=postgres://[USER]:[PASSWORD]@[HOST]/[DB]?sslmode=require
   ```

#### Option C: Aiven (True Dedicated VM)
**Free Tier:** 1 GB storage, 1 GB RAM, 1 CPU

**Benefits:**
- Dedicated virtual machine (not shared serverless)
- Full control over PostgreSQL configuration
- Automatic shutdown after inactivity

**Setup Steps:**
1. Create account at https://aiven.io
2. Create Service → PostgreSQL → Free Tier
3. Enable pgvector extension via service parameters
4. Copy connection URI from Overview
5. Update `.env`:
   ```bash
   DATABASE_URL=[AIVEN_CONNECTION_URI]
   ```

---

### Step 2: Application UI Layer (Streamlit + Agents)

Deploy stateful Streamlit app with agent orchestration to cloud:

#### Option A: Streamlit Community Cloud (Recommended)
**Free Tier:** 1 GB RAM per app, unlimited deployments

**Benefits:**
- Direct GitHub integration (auto-deploy on push)
- WebSocket streaming support for real-time agent output
- No cold starts

**Customization Steps:**
1. Push code to public GitHub repository
2. Visit https://streamlit.io/cloud
3. Connect GitHub → Select repository → Deploy
4. Add secrets: Click "Secrets" → Add `OPENAI_API_KEY`, `DATABASE_URL`, etc.
5. App URL: `https://[YOUR-APP].streamlit.app`

**`.streamlit/secrets.toml` Template:**
```toml
[database]
url = "postgresql://..."

[openai]
api_key = "sk-..."

[auth]
secret_key = "your-secret-key"
```

#### Option B: Hugging Face Spaces
**Free Tier:** CPU containers, ML-focused ecosystem

**Benefits:**
- Native ML library support
- Git-tracked deployment
- Community visibility

**Customization Steps:**
1. Create Space at https://huggingface.co/spaces
2. Choose SDK: Streamlit
3. Connect GitHub or upload files
4. Add repository secrets in Settings
5. App URL: `https://huggingface.co/spaces/[USER]/[SPACE]`

**Requirements:** Add `requirements.txt` to repo root

#### Option C: Render (Traditional PaaS)
**Free Tier:** Web services with 15-min sleep timeout

**Benefits:**
- Dockerfile support
- Custom domain mapping
- Environment variable management

**Customization Steps:**
1. Create account at https://render.com
2. New Web Service → Connect repository
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `streamlit run app.py --server.port=$PORT`
5. Add environment variables in Dashboard
6. **Note:** Free tier sleeps after 15 min inactivity (cold start ~60 sec)

---

### Step 3: MCP Tool Server Layer (Distributed HTTPS)

Convert local stdio MCP servers to remote HTTPS endpoints:

#### Option A: Google Cloud Run (Recommended)
**Free Tier:** 2M requests/month, auto-scale to zero

**Benefits:**
- Container-based deployment
- No background costs (scales to zero)
- Global edge network

**Customization Steps:**
1. Containerize MCP Server:
   ```dockerfile
   # Dockerfile.mcp
   FROM python:3.11-slim
   WORKDIR /app
   COPY fraud_agents/ ./fraud_agents/
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   EXPOSE 8765
   CMD ["python", "-m", "fraud_agents.mcp_server", "--host", "0.0.0.0", "--port", "8765"]
   ```

2. Build & Push:
   ```bash
   docker build -f Dockerfile.mcp -t gcr.io/[PROJECT]/mcp-server .
   docker push gcr.io/[PROJECT]/mcp-server
   ```

3. Deploy to Cloud Run:
   ```bash
   gcloud run deploy mcp-server \
     --image gcr.io/[PROJECT]/mcp-server \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --memory 512Mi \
     --cpu 1 \
     --timeout 300
   ```

4. Update Agent Configuration:
   ```python
   # In prime_agents.py or harness.py
   MCP_ENDPOINT = "https://mcp-server-[HASH].a.run.app"
   ```

#### Option B: Smithery.ai (MCP-Specific Hosting)
**Free Tier:** Community tool hosting

**Benefits:**
- Purpose-built for Model Context Protocol
- Pre-configured tool registry
- Zero deployment complexity

**Customization Steps:**
1. Visit https://smithery.ai
2. Submit GitHub repository URL
3. Configure tool metadata (name, description, inputs/outputs)
4. Deploy → Gets live HTTPS endpoint
5. Reference in agent config:
   ```yaml
   mcp_servers:
     - name: fraud-tools
       url: https://smithery.ai/tools/[YOUR-TOOL]
   ```

#### Option C: Cloudflare Workers (Lightweight Tools)
**Free Tier:** 100K requests/day, edge execution

**Benefits:**
- Sub-millisecond cold starts
- Global edge network (275+ locations)
- TypeScript/WASM support

**Customization Steps:**
1. Rewrite tools as Workers (TypeScript):
   ```typescript
   // worker.ts
   export default {
     async fetch(request: Request) {
       const { tool, params } = await request.json();
       if (tool === 'geo_velocity_check') {
         return Response.json(calculateGeoVelocity(params));
       }
     }
   };
   ```

2. Deploy:
   ```bash
   npm install -g wrangler
   wrangler login
   wrangler deploy
   ```

3. Update agent tool caller to use HTTPS POST instead of stdio

---

### Step 4: End-to-End Cloud Deployment Validation

After migrating all three layers, validate the distributed system:

#### Connectivity Test Script
```python
# tests/cloud/test_cloud_connectivity.py
import os
from fraud_agents.database_prod import ProductionDatabase
from fraud_agents.prime_agents import PrimeSwarmOrchestrator

def test_cloud_database():
    """Verify connection to cloud PostgreSQL"""
    db = ProductionDatabase()
    assert db.is_connected() == True
    print("✅ Cloud DB connected")

def test_cloud_mcp_tools():
    """Verify MCP tools accessible via HTTPS"""
    orchestrator = PrimeSwarmOrchestrator(
        mcp_endpoint=os.getenv("MCP_ENDPOINT")
    )
    result = orchestrator.call_tool('get_customer_profile', {'customer_id': 'CUST001'})
    assert result is not None
    print("✅ MCP tools accessible")

def test_streamlit_frontend():
    """Verify Streamlit app loads with cloud backend"""
    import requests
    app_url = os.getenv("STREAMLIT_APP_URL")
    response = requests.get(f"{app_url}/_stcore/health")
    assert response.status_code == 200
    print("✅ Streamlit frontend healthy")

if __name__ == "__main__":
    test_cloud_database()
    test_cloud_mcp_tools()
    test_streamlit_frontend()
    print("\n🎉 All cloud connectivity tests passed!")
```

#### Run Validation:
```bash
export DATABASE_URL="postgresql://..."
export MCP_ENDPOINT="https://..."
export STREAMLIT_APP_URL="https://..."
python tests/cloud/test_cloud_connectivity.py
```

---

### Cost Optimization Summary

| Component | Local Docker | Cloud Free Tier | Monthly Savings |
|-----------|-------------|-----------------|-----------------|
| Database  | Self-managed | Supabase (500MB) | $0 (vs $25+) |
| App Host  | Self-managed | Streamlit Cloud  | $0 (vs $50+) |
| MCP Tools | Local stdio  | Cloud Run (2M req) | $0 (vs $30+) |
| **Total** | **$0**      | **$0**          | **$105+/mo saved** |

**Scaling Path:** As usage grows beyond free tiers:
- Supabase: $25/mo for 8GB, 2M row reads
- Cloud Run: $0.40 per 1M requests after free quota
- Streamlit: $9/mo per app for Teams features

---

### Hybrid Deployment Strategy

For enterprise clients requiring both pilot flexibility and production scalability:

1. **Week 1-2 (Pilot):** Use Docker Compose locally for rapid iteration
2. **Week 3-4 (Demo):** Deploy to free cloud tiers for client presentations
3. **Month 2+ (Production):** Migrate to paid tiers or private cloud based on volume

**Migration Command:**
```bash
# Export local data
docker-compose exec postgres pg_dump -U postgres fraud_db > backup.sql

# Import to cloud DB
psql "$DATABASE_URL" < backup.sql

# Redeploy app with cloud env vars
git push  # Triggers Streamlit Cloud deploy
```

---

### Troubleshooting Cloud Deployment

| Issue | Solution |
|-------|----------|
| Cold start delays | Use Streamlit Cloud (no sleep) or provision Cloud Run min instances |
| Database connection timeouts | Add `?sslmode=require&connect_timeout=10` to connection string |
| MCP tool latency | Deploy Cloud Run in same region as Streamlit app |
| CORS errors | Configure allowed origins in Cloud Run headers |
| Secrets exposure | Use platform secret managers, never commit `.env` |

---

### Next Steps After Cloud Migration

1. **Monitor Costs:** Set up billing alerts on all platforms
2. **Enable Backups:** Configure automated daily backups (Supabase/Neon include this)
3. **Scale Testing:** Load test with 1000+ concurrent transactions
4. **Compliance Audit:** Verify data residency requirements (choose appropriate regions)
5. **CI/CD Pipeline:** Update GitHub Actions to deploy to cloud targets

**Documentation Links:**
- Supabase pgvector: https://supabase.com/docs/guides/database/vector-columns
- Neon Branching: https://neon.tech/docs/branching/overview
- Streamlit Secrets: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management
- Cloud Run Deployment: https://cloud.google.com/run/docs/deploying
