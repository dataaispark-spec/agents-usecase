"""
Production Database Layer using PostgreSQL + pgvector.
Replaces SQLite for enterprise-scale transaction volumes and semantic memory.
"""
import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from pgvector.psycopg2 import register_vector

logger = logging.getLogger(__name__)

class ProductionDatabase:
    def __init__(self):
        self.conn = None
        self.connect()
        self._initialize_schema()
    
    def connect(self):
        """Establish connection to PostgreSQL with pgvector support."""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "clerivon_fraud"),
            user=os.getenv("DB_USER", "clerivon_user"),
            password=os.getenv("DB_PASSWORD", "secure_password_here"),
            cursor_factory=RealDictCursor
        )
        register_vector(self.conn)
        logger.info("Connected to PostgreSQL with pgvector support")
    
    def _initialize_schema(self):
        """Create tables if they don't exist."""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Transactions table
            cur.execute("""
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
            """)
            
            # Cases table
            cur.execute("""
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
            """)
            
            # Flywheel feedback table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS flywheel_feedback (
                    id SERIAL PRIMARY KEY,
                    case_id VARCHAR(50) REFERENCES cases(case_id),
                    feedback_type VARCHAR(20),
                    original_threshold FLOAT,
                    adjusted_threshold FLOAT,
                    feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    analyst_id VARCHAR(50)
                );
            """)
            
            # Audit log for compliance
            cur.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(50),
                    entity_id VARCHAR(50),
                    old_value JSONB,
                    new_value JSONB,
                    user_id VARCHAR(50),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.conn.commit()
        logger.info("Database schema initialized")
    
    def insert_transaction(self, tx_data: Dict[str, Any]) -> str:
        """Insert a new transaction."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transactions 
                (tx_id, customer_id, amount, merchant_name, mcc_code, 
                 location_lat, location_lon, device_id, risk_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING tx_id
            """, (
                tx_data['tx_id'], tx_data['customer_id'], tx_data['amount'],
                tx_data.get('merchant_name'), tx_data.get('mcc_code'),
                tx_data.get('location_lat'), tx_data.get('location_lon'),
                tx_data.get('device_id'), tx_data.get('risk_score')
            ))
            tx_id = cur.fetchone()['tx_id']
            self.conn.commit()
            return tx_id
    
    def create_case(self, case_data: Dict[str, Any]) -> str:
        """Create a new fraud case."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO cases 
                (case_id, tx_id, assigned_agent, evidence_json, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING case_id
            """, (
                case_data['case_id'], case_data['tx_id'],
                case_data.get('assigned_agent'),
                json.dumps(case_data.get('evidence', {})),
                case_data.get('status', 'OPEN')
            ))
            case_id = cur.fetchone()['case_id']
            self.conn.commit()
            
            # Log audit
            self._log_audit("CASE_CREATED", case_id, None, case_data)
            return case_id
    
    def update_case_decision(self, case_id: str, decision: str, analyst_id: str):
        """Update case with human decision."""
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE cases 
                SET decision = %s, analyst_id = %s, 
                    reviewed_at = CURRENT_TIMESTAMP, status = 'CLOSED'
                WHERE case_id = %s
            """, (decision, analyst_id, case_id))
            self.conn.commit()
            
            self._log_audit("CASE_DECISION", case_id, None, {
                "decision": decision, "analyst_id": analyst_id
            })
    
    def record_flywheel_feedback(self, case_id: str, feedback_type: str, 
                                  old_threshold: float, new_threshold: float, 
                                  analyst_id: str):
        """Record feedback for continuous learning."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO flywheel_feedback 
                (case_id, feedback_type, original_threshold, adjusted_threshold, analyst_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (case_id, feedback_type, old_threshold, new_threshold, analyst_id))
            
            # Mark case as false positive if applicable
            if feedback_type == "FALSE_POSITIVE":
                cur.execute("""
                    UPDATE cases SET is_false_positive = TRUE WHERE case_id = %s
                """, (case_id,))
            
            self.conn.commit()
    
    def get_recent_cases(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent cases for dashboard."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT c.*, t.amount, t.merchant_name, t.timestamp as tx_time
                FROM cases c
                JOIN transactions t ON c.tx_id = t.tx_id
                ORDER BY c.created_at DESC
                LIMIT %s
            """, (limit,))
            return [dict(row) for row in cur.fetchall()]
    
    def search_similar_transactions(self, embedding: List[float], limit: int = 5) -> List[Dict]:
        """Semantic search for similar past transactions using pgvector."""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT tx_id, customer_id, amount, merchant_name, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM transactions
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> %s::vector
                LIMIT %s
            """, (embedding, embedding, limit))
            return [dict(row) for row in cur.fetchall()]
    
    def _log_audit(self, event_type: str, entity_id: str, 
                   old_value: Optional[Dict], new_value: Optional[Dict], 
                   user_id: str = "system"):
        """Log audit trail for compliance."""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO audit_log 
                (event_type, entity_id, old_value, new_value, user_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (event_type, entity_id, 
                  json.dumps(old_value) if old_value else None,
                  json.dumps(new_value) if new_value else None,
                  user_id))
            self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

# Singleton instance
db = ProductionDatabase()
