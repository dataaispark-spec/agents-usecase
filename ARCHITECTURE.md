# Clerivon AI - Multi-Agent Fraud Detection Architecture

## Complete Implementation Guide with Data Flow & Step-by-Step Fraud Detection

---

## Table of Contents

1. Executive Summary
2. System Architecture Overview
3. Dataset Integration & Mapping
4. Multi-Agent System Deep Dive
5. Harness Engineering Components
6. Step-by-Step Fraud Detection Walkthrough
7. Deployment Guide
8. Testing & Validation
9. End User Guide

---

## 1. Executive Summary

**Clerivon AI** is an enterprise-grade, multi-agent fraud detection system built on the **Agent = Model + Harness** architecture. The system processes real-time financial transactions through specialized AI agents.

### Key Capabilities

| Capability | Description | Business Impact |
|------------|-------------|-----------------|
| Real-Time Adjudication | Process transactions in <500ms with 5-agent pipeline | Reduce fraud losses by 60% |
| Multi-Dataset Support | PaySim, IEEE-CIS, BAF, Credit Card ULB datasets | Unified fraud detection |
| Closed-Loop Learning | Flywheel learns from every human decision | False positives drop 4% daily |
| Enterprise Security | SSO/RBAC, air-gapped deployment, PII redaction | SOC2, GDPR, PCI-DSS compliant |
| Explainable AI | Full evidence trail with reasoning scores | Pass regulatory audits |

---

## 2. System Architecture Overview

```
DATA INGESTION LAYER
├── PaySim (Mobile Money)
├── IEEE-CIS (Card-Not-Present)
├── BAF (KYC/Identity)
└── Credit Card ULB (Anomaly Detection)
        │
        ▼
HARNESS ENGINEERING LAYER
├── Guardrails Engine (PII, Injection Defense)
├── Memory Engine (Context + Vector Search)
├── Verification Engine (Validation + Self-Correct)
└── Observability Engine (Tracing + Metrics)
        │
        ▼
MULTI-AGENT SWARM
MONITOR → INVESTIGATOR (6 Tools) → ADJUDICATOR → EXPLAINER → FEEDBACK
        │
        ▼
ENTERPRISE INTEGRATION
├── MCP Server (Tools API)
├── SSO/RBAC Auth
├── PostgreSQL + pgvector
└── Streamlit UI
```

---

## 3. Dataset Integration & Mapping

### Supported Datasets

#### PaySim Mobile Money
- **Use Case:** P2P Transfer Fraud
- **Volume:** 6.3M rows, 30 days
- **Features:** step, type, amount, nameOrig, nameDest, balances
- **Target Agents:** Ledger Audit, User Behavior

#### IEEE-CIS Fraud Detection
- **Use Case:** CNP E-Commerce Fraud
- **Volume:** 1M rows
- **Features:** Device fingerprints, IP, email domain, card BIN
- **Target Agents:** Device/Network, Adjudication

#### Bank Account Fraud (BAF)
- **Use Case:** Synthetic Identity/KYC Fraud
- **Volume:** 1M applications
- **Features:** Demographics, income, credit score, application frequency
- **Target Agents:** KYC/Identity, Underwriting

#### Credit Card ULB
- **Use Case:** Card Anomaly Detection
- **Volume:** 284K transactions
- **Features:** 28 PCA vectors, amount, time
- **Target Agents:** User Behavior, Adjudication

---

## 4. Multi-Agent System Deep Dive

### 5-Agent Pipeline

1. **Monitor Agent** (<50ms)
   - First-line anomaly detection
   - Rule-based thresholds + statistical anomalies

2. **Investigator Agent** (<300ms)
   - Calls 6 MCP tools:
     - get_customer_profile()
     - get_device_history()
     - calculate_geo_velocity()
     - check_merchant_risk()
     - get_recent_transactions()
     - check_sanctions_list()

3. **Adjudicator Agent** (<100ms)
   - Makes final decision: BLOCK/REVIEW/APPROVE
   - Weighted evidence scoring

4. **Explainer Agent**
   - Generates human-readable rationale
   - Structured JSON + natural language

5. **Feedback Agent**
   - Closed-loop learning (Flywheel)
   - Adjusts thresholds based on overrides

---

## 5. Harness Engineering Components

### Formula: Agent = Model + Harness

The harness wraps around AI models for enterprise reliability.

### Four Engines

1. **Guardrails Engine**
   - PII redaction (SSN, credit cards, emails)
   - Prompt injection defense
   - Output compliance (GDPR, PCI-DSS)

2. **Memory Engine**
   - Short-term context (conversation history)
   - Long-term vector search (pgvector)

3. **Verification Engine**
   - Decision validation
   - Evidence requirements
   - Self-correction triggers

4. **Observability Engine**
   - Distributed tracing
   - Latency metrics
   - Audit logging

---

## 6. Step-by-Step Fraud Detection Walkthrough

### Scenario: Impossible Travel Fraud

**Transaction Details:**
- Customer: CUST_789456
- Amount: $2,450.00
- Location: Singapore (SG)
- Time: 14:32 UTC

**Previous Transaction:**
- Location: London (UK)
- Time: 14:02 UTC (30 minutes ago)
- Distance: 6,765 miles

### Step 1: Monitor Agent Flags Transaction

```json
{
  "transaction_id": "TXN_987654321",
  "risk_score": 0.87,
  "flags": ["high_amount", "geo_anomaly"],
  "action": "FLAG_FOR_REVIEW"
}
```

### Step 2: Investigator Agent Gathers Evidence

**Tool Call 1: get_customer_profile()**
```json
{
  "customer_id": "CUST_789456",
  "risk_tier": "STANDARD",
  "account_age_days": 847,
  "historical_fraud": false
}
```

**Tool Call 2: calculate_geo_velocity()**
```json
{
  "origin": {"city": "London", "country": "UK", "time": "14:02"},
  "destination": {"city": "Singapore", "country": "SG", "time": "14:32"},
  "distance_miles": 6765,
  "time_minutes": 30,
  "required_speed_mph": 13530,
  "physically_possible": false,
  "impossible_travel_score": 0.98
}
```

**Tool Call 3: get_device_history()**
```json
{
  "device_id": "DEV_456789",
  "first_seen": "2023-06-15",
  "previous_locations": ["London", "Manchester", "Birmingham"],
  "new_location": "Singapore",
  "location_anomaly": true
}
```

**Tool Call 4: check_merchant_risk()**
```json
{
  "merchant_id": "MERCH_12345",
  "mcc_code": "5944",
  "category": "Jewelry Store",
  "risk_score": 0.72,
  "chargeback_rate": 0.034
}
```

**Tool Call 5: get_recent_transactions()**
```json
{
  "last_24h_count": 3,
  "last_24h_amount": 3127.50,
  "average_daily_count": 1.2,
  "velocity_anomaly": true
}
```

**Tool Call 6: check_sanctions_list()**
```json
{
  "customer_name": "John Smith",
  "sanctions_match": false,
  "pep_match": false,
  "ofac_match": false
}
```

### Step 3: Adjudicator Agent Makes Decision

**Evidence Scoring:**
- Impossible travel: +25 points
- Device location anomaly: +15 points
- High merchant risk: +10 points
- Velocity anomaly: +8 points
- Clean sanctions check: -5 points
- Long account history: -3 points

**Total Score:** 50 points (Threshold: 40 = BLOCK)

**Decision:**
```json
{
  "action": "BLOCK",
  "confidence": 0.92,
  "reasoning": "Impossible travel detected with supporting evidence",
  "evidence_summary": [
    "Customer transacted in London 30 min ago",
    "Distance 6,765 miles requires 13,530 mph",
    "Device never seen in Singapore before",
    "High-risk jewelry merchant"
  ]
}
```

### Step 4: Explainer Agent Generates Rationale

**Human-Readable Summary:**
```
FRAUD ALERT - CASE #CASE_20240115_001

Customer: John Smith (CUST_789456)
Transaction: $2,450.00 at Luxury Gems Jewelry, Singapore
Time: 2024-01-15 14:32 UTC

DECISION: BLOCK

KEY FINDINGS:
1. IMPOSSIBLE TRAVEL: Customer was in London, UK at 14:02 UTC 
   (30 minutes ago). Distance to Singapore is 6,765 miles, 
   requiring travel speed of 13,530 mph - physically impossible.

2. DEVICE ANOMALY: Device DEV_456789 has only been used in 
   UK cities (London, Manchester, Birmingham). First appearance 
   in Singapore.

3. MERCHANT RISK: Jewelry stores have elevated chargeback rates 
   (3.4% vs 1.2% average).

4. VELOCITY ANOMALY: 3 transactions in 24 hours ($3,127.50) 
   vs customer average of 1.2 transactions daily.

RECOMMENDATION: Block transaction and contact customer to 
verify identity. Potential account takeover or compromised 
credentials.
```

### Step 5: Human Analyst Review

**Analyst Actions:**
- Opens case in Streamlit UI
- Reviews evidence drawer
- Confirms fraud decision
- Adds note: "Called customer - confirmed unauthorized transaction"

### Step 6: Feedback Agent Updates Flywheel

**Learning Actions:**
- Increments true positive counter
- Adjusts impossible travel threshold: 0.95 → 0.93
- Updates merchant risk weights
- Logs feedback event for audit

**Metrics Updated:**
```json
{
  "true_positives": 847,
  "false_positives": 123,
  "precision": 0.873,
  "recall": 0.891,
  "threshold_adjustments_today": 12
}
```

---

## 7. Deployment Guide

### Quick Start (Docker Compose)

```bash
# Clone repository
git clone https://github.com/clerivon/fraud-detection.git
cd fraud-detection

# Configure environment
cp .env.example .env
# Edit with your database credentials, API keys

# Deploy entire stack
docker-compose up -d

# Access services
# Streamlit UI: http://localhost:8501
# PostgreSQL: localhost:5432
# MCP Server: localhost:8765
```

### Production Deployment Options

#### Option 1: Docker Compose (Single Node)
- Best for: Pilots, small teams
- Capacity: Up to 100 txn/s
- Resources: 8 CPU, 16GB RAM

#### Option 2: Kubernetes (Multi-Node)
- Best for: Enterprise production
- Capacity: 1000+ txn/s
- Auto-scaling enabled

#### Option 3: Air-Gapped Deployment
- Export Docker images: `docker save clerivon-app > app.tar`
- Transfer via secure media
- Load in isolated environment: `docker load < app.tar`

---

## 8. Testing & Validation

### Run Test Suite

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v --cov=fraud_agents

# Run specific test categories
pytest tests/test_harness.py -v
pytest tests/test_agents.py -v
pytest tests/test_data_pipeline.py -v
```

### Validate Data Pipeline

```bash
python -m fraud_agents.data_pipeline
```

Expected output:
- Stream processing demo
- Batch processing demo
- Data quality validation
- Agent routing verification

### Performance Benchmarks

```bash
# Load testing
python benchmarks/latency_test.py
python benchmarks/throughput_test.py
```

Targets:
- P95 latency < 500ms
- Throughput > 1000 txn/s
- Error rate < 0.1%

---

## 9. End User Guide

### For Fraud Analysts

**Daily Workflow:**
1. Login via SSO (Azure AD / Okta / Keycloak)
2. Open "Case Review" tab
3. Review flagged cases (HIGH → MEDIUM → LOW priority)
4. Examine evidence drawer for each case
5. Make decision: Confirm Fraud / False Positive / Escalate
6. Monitor Flywheel Analytics for impact

**Keyboard Shortcuts:**
- `C` = Confirm Fraud
- `F` = Mark False Positive
- `E` = Escalate
- `N` = Add Note

### For Managers

**Dashboard Views:**
- Operations: Cases processed, handling time, queue depth
- Performance: Detection rate, false positive rate, $ saved
- Team: Analyst productivity, escalations, training needs

**Approval Workflows:**
- Senior analysts can override junior decisions
- Managers can adjust thresholds and export compliance reports

### For Administrators

**System Configuration:**
```bash
# Create new user
python manage.py create_user --username jsmith --role SENIOR_ANALYST

# Export compliance report
python manage.py export_compliance --report-type sox --date-range 2024-01

# Monitor system health
kubectl get pods -n clerivon
kubectl logs -f deployment/fraud-agents
```

**Alerting Rules:**
- False positive rate > 20% for 15 minutes
- P95 latency > 500ms for 5 minutes
- Error rate > 1% for 10 minutes

---

## Support

- Documentation: https://docs.clerivon.ai
- Email: support@clerivon.ai
- Status Page: https://status.clerivon.ai
