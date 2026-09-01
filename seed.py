"""
Seed sample cases for Clerivon lab/pilot.
Uses db_factory (sqlite default, postgres when DB_BACKEND=postgres).

  python seed.py
"""
from __future__ import annotations

import os
import random
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fraud_agents.agents import FraudDetectionPipeline, Transaction
from fraud_agents.db_factory import db as get_db


def create_sample_transactions():
    return [
        {
            "name": "Impossible Travel - High Risk",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST001",
                amount=4500.00,
                currency="USD",
                merchant_id="MERCH-5521",
                mcc_code="5944",
                location="Singapore",
                timestamp=datetime.now(),
                device_id="DEV99999",
            ),
        },
        {
            "name": "High-Value Gambling",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST002",
                amount=8500.00,
                currency="USD",
                merchant_id="MERCH-7832",
                mcc_code="7995",
                location="Tokyo",
                timestamp=datetime.now(),
                device_id="DEV99999",
            ),
        },
        {
            "name": "Normal Grocery Purchase",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST003",
                amount=185.50,
                currency="USD",
                merchant_id="MERCH-1234",
                mcc_code="5411",
                location="Singapore",
                timestamp=datetime.now(),
                device_id="DEV67890",
            ),
        },
        {
            "name": "Behavioral Anomaly",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST001",
                amount=2500.00,
                currency="USD",
                merchant_id="MERCH-4421",
                mcc_code="5812",
                location="London",
                timestamp=datetime.now(),
                device_id="DEV12345",
            ),
        },
    ]


def main():
    print(f"Clerivon seed (DB_BACKEND={os.getenv('DB_BACKEND', 'sqlite')})")
    pipeline = FraudDetectionPipeline()
    database = get_db()
    scenarios = create_sample_transactions()
    created = 0
    for scenario in scenarios:
        print(f"Processing: {scenario['name']}")
        result = pipeline.process_transaction(scenario["transaction"])
        if result.get("status") == "AUTO_APPROVED":
            print("  auto-approved")
            continue
        case_file = result.get("case_file")
        if case_file and database.save_case(case_file):
            created += 1
            print(f"  case {case_file.get('case_id')} decision={result.get('decision')}")
        else:
            print("  save failed or no case")
    print(f"Seed complete. cases_created={created}")
    print(database.get_flywheel_metrics())


if __name__ == "__main__":
    main()
