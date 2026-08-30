"""
Database layer for Fraud Detection System
Uses SQLite for demo, designed for pgvector upgrade
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class Database:
    """SQLite database wrapper for fraud cases."""
    
    def __init__(self, db_path: str = "fraud_cases.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize database tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Cases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                transaction_id TEXT,
                customer_id TEXT,
                amount REAL,
                location TEXT,
                timestamp TEXT,
                ai_decision TEXT,
                human_decision TEXT,
                status TEXT,
                risk_score INTEGER,
                created_at TEXT,
                reviewed_at TEXT
            )
        ''')
        
        # Agent responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                agent_name TEXT,
                action TEXT,
                reasoning TEXT,
                evidence TEXT,
                risk_contribution INTEGER,
                timestamp TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                human_decision TEXT,
                ai_decision TEXT,
                agreement BOOLEAN,
                analyst_notes TEXT,
                learning_action TEXT,
                adjustment TEXT,
                created_at TEXT,
                FOREIGN KEY (case_id) REFERENCES cases(case_id)
            )
        ''')
        
        # Flywheel metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS flywheel_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_case(self, case_file: Dict[str, Any]) -> bool:
        """Save a case to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert case
            cursor.execute('''
                INSERT OR REPLACE INTO cases 
                (case_id, transaction_id, customer_id, amount, location, timestamp,
                 ai_decision, human_decision, status, risk_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_file.get("case_id"),
                case_file.get("transaction_summary", {}).get("transaction_id"),
                case_file.get("transaction_summary", {}).get("customer_id"),
                case_file.get("transaction_summary", {}).get("amount"),
                case_file.get("transaction_summary", {}).get("location"),
                case_file.get("transaction_summary", {}).get("timestamp"),
                case_file.get("final_decision"),
                None,
                "PENDING_REVIEW",
                case_file.get("risk_assessment", {}).get("total_risk_score"),
                datetime.now().isoformat()
            ))
            
            # Insert agent responses
            evidence_trail = case_file.get("evidence_trail", {})
            for agent_name, response in evidence_trail.items():
                cursor.execute('''
                    INSERT INTO agent_responses 
                    (case_id, agent_name, action, reasoning, evidence, risk_contribution, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    case_file.get("case_id"),
                    response.get("agent_name"),
                    response.get("action"),
                    response.get("reasoning"),
                    json.dumps(response.get("evidence", {})),
                    response.get("risk_score_contribution"),
                    response.get("timestamp")
                ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving case: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def update_human_decision(self, case_id: str, human_decision: str) -> bool:
        """Update human decision for a case."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE cases 
                SET human_decision = ?, status = 'REVIEWED', reviewed_at = ?
                WHERE case_id = ?
            ''', (human_decision, datetime.now().isoformat(), case_id))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating decision: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def save_feedback(self, case_id: str, feedback_data: Dict[str, Any]) -> bool:
        """Save feedback to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            entry = feedback_data.get("feedback_entry", {})
            cursor.execute('''
                INSERT INTO feedback 
                (case_id, human_decision, ai_decision, agreement, analyst_notes,
                 learning_action, adjustment, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_id,
                entry.get("human_decision"),
                entry.get("ai_decision"),
                entry.get("agreement"),
                entry.get("analyst_notes"),
                feedback_data.get("learning_action"),
                feedback_data.get("adjustment"),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def get_pending_cases(self) -> List[Dict[str, Any]]:
        """Get all pending cases."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cases WHERE status = 'PENDING_REVIEW' ORDER BY created_at DESC
        ''')
        
        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cases
    
    def get_all_cases(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent cases."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM cases ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        cases = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return cases
    
    def get_case_details(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed case information."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get case
        cursor.execute('SELECT * FROM cases WHERE case_id = ?', (case_id,))
        case_row = cursor.fetchone()
        
        if not case_row:
            conn.close()
            return None
        
        case = dict(case_row)
        
        # Get agent responses
        cursor.execute('''
            SELECT * FROM agent_responses WHERE case_id = ? ORDER BY id
        ''', (case_id,))
        
        case["agent_responses"] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return case
    
    def get_flywheel_metrics(self) -> Dict[str, Any]:
        """Get flywheel learning metrics."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Total cases
        cursor.execute('SELECT COUNT(*) as count FROM cases')
        total_cases = cursor.fetchone()["count"]
        
        # Reviewed cases
        cursor.execute('SELECT COUNT(*) as count FROM cases WHERE status = "REVIEWED"')
        reviewed_cases = cursor.fetchone()["count"]
        
        # Agreement rate
        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE agreement = 1')
        agreements = cursor.fetchone()["count"]
        
        cursor.execute('SELECT COUNT(*) as count FROM feedback')
        total_feedback = cursor.fetchone()["count"]
        
        agreement_rate = (agreements / total_feedback * 100) if total_feedback > 0 else 0
        
        # False positives/negatives
        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE adjustment = "INCREASE_THRESHOLD"')
        false_positives = cursor.fetchone()["count"]
        
        cursor.execute('SELECT COUNT(*) as count FROM feedback WHERE adjustment = "DECREASE_THRESHOLD"')
        false_negatives = cursor.fetchone()["count"]
        
        conn.close()
        
        return {
            "total_cases": total_cases,
            "reviewed_cases": reviewed_cases,
            "pending_cases": total_cases - reviewed_cases,
            "agreement_rate": round(agreement_rate, 2),
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "total_feedback": total_feedback
        }
    
    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent feedback entries."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM feedback ORDER BY created_at DESC LIMIT ?
        ''', (limit,))
        
        feedback = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return feedback


# Singleton instance
db = Database()
