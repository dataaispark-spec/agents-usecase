"""
Lab Postgres adapter with the *same method surface* as SQLite Database
so app.py / seed.py work without changes when DB_BACKEND=postgres.

Schema is intentionally aligned with the SQLite demo tables (not the
older divergent database_prod.py transaction/embedding schema).
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class LabPostgresDatabase:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            dbname=os.getenv("DB_NAME", "clerivon_fraud"),
            user=os.getenv("DB_USER", "clerivon_user"),
            password=os.getenv("DB_PASSWORD", "secure_password_change_in_prod"),
        )
        self.conn.autocommit = False
        self.init_db()

    def init_db(self) -> None:
        with self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    transaction_id TEXT,
                    customer_id TEXT,
                    amount DOUBLE PRECISION,
                    location TEXT,
                    timestamp TEXT,
                    ai_decision TEXT,
                    human_decision TEXT,
                    status TEXT,
                    risk_score INTEGER,
                    created_at TEXT,
                    reviewed_at TEXT
                );
                CREATE TABLE IF NOT EXISTS agent_responses (
                    id SERIAL PRIMARY KEY,
                    case_id TEXT REFERENCES cases(case_id),
                    agent_name TEXT,
                    action TEXT,
                    reasoning TEXT,
                    evidence TEXT,
                    risk_contribution INTEGER,
                    timestamp TEXT
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    id SERIAL PRIMARY KEY,
                    case_id TEXT REFERENCES cases(case_id),
                    human_decision TEXT,
                    ai_decision TEXT,
                    agreement BOOLEAN,
                    analyst_notes TEXT,
                    learning_action TEXT,
                    adjustment TEXT,
                    created_at TEXT
                );
                """
            )
            self.conn.commit()
        logger.info("Lab Postgres schema ready")

    def save_case(self, case_file: Dict[str, Any]) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO cases
                    (case_id, transaction_id, customer_id, amount, location, timestamp,
                     ai_decision, human_decision, status, risk_score, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (case_id) DO UPDATE SET
                      ai_decision = EXCLUDED.ai_decision,
                      risk_score = EXCLUDED.risk_score,
                      status = EXCLUDED.status
                    """,
                    (
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
                        datetime.now().isoformat(),
                    ),
                )
                for _, response in (case_file.get("evidence_trail") or {}).items():
                    cur.execute(
                        """
                        INSERT INTO agent_responses
                        (case_id, agent_name, action, reasoning, evidence, risk_contribution, timestamp)
                        VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """,
                        (
                            case_file.get("case_id"),
                            response.get("agent_name"),
                            response.get("action"),
                            response.get("reasoning"),
                            json.dumps(response.get("evidence", {})),
                            response.get("risk_score_contribution"),
                            response.get("timestamp"),
                        ),
                    )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("save_case failed: %s", e)
            return False

    def update_human_decision(self, case_id: str, human_decision: str) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE cases SET human_decision=%s, status='REVIEWED', reviewed_at=%s
                    WHERE case_id=%s
                    """,
                    (human_decision, datetime.now().isoformat(), case_id),
                )
                self.conn.commit()
                return cur.rowcount > 0
        except Exception as e:
            self.conn.rollback()
            logger.error("update_human_decision failed: %s", e)
            return False

    def save_feedback(self, case_id: str, feedback_data: Dict[str, Any]) -> bool:
        try:
            entry = feedback_data.get("feedback_entry", {})
            with self.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO feedback
                    (case_id, human_decision, ai_decision, agreement, analyst_notes,
                     learning_action, adjustment, created_at)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        case_id,
                        entry.get("human_decision"),
                        entry.get("ai_decision"),
                        entry.get("agreement"),
                        entry.get("analyst_notes"),
                        feedback_data.get("learning_action"),
                        feedback_data.get("adjustment"),
                        datetime.now().isoformat(),
                    ),
                )
                self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error("save_feedback failed: %s", e)
            return False

    def get_pending_cases(self) -> List[Dict[str, Any]]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM cases WHERE status='PENDING_REVIEW' ORDER BY created_at DESC"
            )
            return [dict(r) for r in cur.fetchall()]

    def get_case_details(self, case_id: str) -> Optional[Dict[str, Any]]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM cases WHERE case_id=%s", (case_id,))
            row = cur.fetchone()
            if not row:
                return None
            case = dict(row)
            cur.execute(
                "SELECT * FROM agent_responses WHERE case_id=%s ORDER BY id", (case_id,)
            )
            case["agent_responses"] = [dict(r) for r in cur.fetchall()]
            return case

    def get_flywheel_metrics(self) -> Dict[str, Any]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS c FROM cases")
            total = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) AS c FROM cases WHERE status='REVIEWED'")
            reviewed = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) AS c FROM feedback WHERE agreement IS TRUE")
            agreements = cur.fetchone()["c"]
            cur.execute("SELECT COUNT(*) AS c FROM feedback")
            total_fb = cur.fetchone()["c"]
            cur.execute(
                "SELECT COUNT(*) AS c FROM feedback WHERE adjustment='INCREASE_THRESHOLD'"
            )
            fps = cur.fetchone()["c"]
            cur.execute(
                "SELECT COUNT(*) AS c FROM feedback WHERE adjustment='DECREASE_THRESHOLD'"
            )
            fns = cur.fetchone()["c"]
        rate = (agreements / total_fb * 100) if total_fb else 0
        return {
            "total_cases": total,
            "reviewed_cases": reviewed,
            "pending_cases": total - reviewed,
            "agreement_rate": round(rate, 2),
            "false_positives": fps,
            "false_negatives": fns,
            "total_feedback": total_fb,
        }

    def get_recent_feedback(self, limit: int = 10) -> List[Dict[str, Any]]:
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM feedback ORDER BY created_at DESC LIMIT %s", (limit,)
            )
            return [dict(r) for r in cur.fetchall()]
