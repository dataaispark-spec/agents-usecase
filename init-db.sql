-- Initialize PostgreSQL Database with pgvector
-- Run automatically on first container start

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create database (if not exists)
-- Note: Database creation must be done before connecting

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE clerivon_fraud TO clerivon_user;

-- Connect to the specific database for table creation
\c clerivon_fraud

-- Transactions table with vector embedding for semantic search
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    tx_id VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    merchant_name VARCHAR(255),
    mcc_code VARCHAR(10),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    location_lat FLOAT,
    location_lon FLOAT,
    device_id VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    risk_score FLOAT,
    embedding vector(384)
);

-- Cases table for fraud investigations
CREATE TABLE IF NOT EXISTS cases (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) UNIQUE NOT NULL,
    tx_id VARCHAR(50) REFERENCES transactions(tx_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN',
    assigned_agent VARCHAR(50),
    evidence_json JSONB,
    decision VARCHAR(20),
    analyst_id VARCHAR(50),
    reviewed_at TIMESTAMP,
    is_false_positive BOOLEAN DEFAULT FALSE
);

-- Flywheel feedback table for continuous learning
CREATE TABLE IF NOT EXISTS flywheel_feedback (
    id SERIAL PRIMARY KEY,
    case_id VARCHAR(50) REFERENCES cases(case_id),
    feedback_type VARCHAR(20),
    original_threshold FLOAT,
    adjusted_threshold FLOAT,
    feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyst_id VARCHAR(50)
);

-- Audit log for compliance and regulatory requirements
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    entity_id VARCHAR(50),
    old_value JSONB,
    new_value JSONB,
    user_id VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id);
CREATE INDEX IF NOT EXISTS idx_transactions_timestamp ON transactions(timestamp);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_tx_id ON cases(tx_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);

-- Vector similarity index for semantic search
CREATE INDEX IF NOT EXISTS idx_transactions_embedding 
ON transactions USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Grant table permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO clerivon_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO clerivon_user;

-- Insert sample data for testing (optional - comment out in production)
-- INSERT INTO transactions (tx_id, customer_id, amount, merchant_name, mcc_code, location_lat, location_lon, device_id, risk_score)
-- VALUES 
-- ('tx_001', 'cust_123', 150.00, 'Amazon', '5411', 51.5074, -0.1278, 'dev_abc123', 0.15),
-- ('tx_002', 'cust_456', 2500.00, 'Electronics Store', '5732', 40.7128, -74.0060, 'dev_xyz789', 0.75);
