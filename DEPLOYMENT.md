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
