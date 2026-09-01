"""
Database factory for Clerivon lab/pilot.

DB_BACKEND=sqlite (default)  → fraud_agents.database.Database (file)
DB_BACKEND=postgres          → fraud_agents.database_lab_pg.LabPostgresDatabase

Lab pilot recommendation: sqlite + Docker volume (zero friction).
Postgres is optional when you need multi-container shared state.
"""
from __future__ import annotations

import os


def get_db():
    backend = os.getenv("DB_BACKEND", "sqlite").strip().lower()
    if backend in ("postgres", "postgresql", "pg"):
        from fraud_agents.database_lab_pg import LabPostgresDatabase

        return LabPostgresDatabase()
    from fraud_agents.database import Database

    path = os.getenv("FRAUD_DB_PATH", "fraud_cases.db")
    return Database(db_path=path)


# Lazy singleton used by app/seed
_db = None


def db():
    global _db
    if _db is None:
        _db = get_db()
    return _db
