#!/usr/bin/env python3
"""
Headless DEMO.md path (no Streamlit browser required).

  PYTHONPATH=. python scripts/demo_emulator.py
"""
from __future__ import annotations

import os
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main() -> int:
    from fraud_agents.agents import FraudDetectionPipeline, Transaction
    from fraud_agents.db_factory import db as get_db

    pipeline = FraudDetectionPipeline()
    database = get_db()

    print("=== DEMO EMULATOR: impossible_travel ===")
    txn = Transaction(
        transaction_id="TXN-EMULATOR-001",
        customer_id="CUST001",
        amount=4500.0,
        currency="USD",
        merchant_id="MERCH-DEMO",
        mcc_code="5944",
        location="Singapore",
        timestamp=datetime.now(),
        device_id="DEV99999",
    )
    result = pipeline.process_transaction(txn)
    print(f"  status={result.get('status')} decision={result.get('decision')}")
    case = result.get("case_file")
    if not case:
        print("FAIL: expected case_file")
        return 1
    if not database.save_case(case):
        print("FAIL: save_case")
        return 1
    case_id = case["case_id"]
    print(f"  case saved: {case_id}")
    print(f"  risk={case['risk_assessment']['total_risk_score']}")

    print("=== Case Review: Confirm AI ===")
    ai = case["final_decision"]
    database.update_human_decision(case_id, ai)
    fb = pipeline.submit_feedback(case_id, ai, ai, "Analyst confirmed (emulator)")
    database.save_feedback(case_id, fb)
    print(f"  feedback: {fb.get('learning_action')} / {fb.get('adjustment')}")

    print("=== Flywheel ===")
    m = database.get_flywheel_metrics()
    print(f"  metrics: {m}")

    print("=== Contrast: normal grocery ===")
    txn2 = Transaction(
        transaction_id="TXN-EMULATOR-002",
        customer_id="CUST003",
        amount=185.5,
        currency="USD",
        merchant_id="MERCH-G",
        mcc_code="5411",
        location="Singapore",
        timestamp=datetime.now(),
        device_id="DEV67890",
    )
    r2 = pipeline.process_transaction(txn2)
    print(f"  status={r2.get('status')} decision={r2.get('decision')}")

    print("\n*** DEMO EMULATOR: ALL OK ***")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
