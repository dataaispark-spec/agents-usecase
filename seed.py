"""
Seed script to populate database with sample cases for demo
Run: python seed.py
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fraud_agents.agents import FraudDetectionPipeline, Transaction
from fraud_agents.database import db


def create_sample_transactions():
    """Create diverse sample transactions for demo."""
    
    scenarios = [
        {
            "name": "Impossible Travel - High Risk",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST001",
                amount=4500.00,
                currency="USD",
                merchant_id="MERCH-5521",
                mcc_code="5944",  # Jewelry
                location="Singapore",
                timestamp=datetime.now(),
                device_id="DEV99999"
            ),
            "expected_decision": "BLOCK"
        },
        {
            "name": "High-Value Gambling",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST002",
                amount=8500.00,
                currency="USD",
                merchant_id="MERCH-7832",
                mcc_code="7995",  # Gambling
                location="Tokyo",
                timestamp=datetime.now(),
                device_id="DEV99999"
            ),
            "expected_decision": "BLOCK"
        },
        {
            "name": "Normal Grocery Purchase",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST003",
                amount=185.50,
                currency="USD",
                merchant_id="MERCH-1234",
                mcc_code="5411",  # Grocery
                location="Singapore",
                timestamp=datetime.now(),
                device_id="DEV67890"
            ),
            "expected_decision": "APPROVE"
        },
        {
            "name": "Behavioral Anomaly",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST001",
                amount=2500.00,
                currency="USD",
                merchant_id="MERCH-4421",
                mcc_code="5812",  # Restaurant
                location="London",
                timestamp=datetime.now(),
                device_id="DEV12345"
            ),
            "expected_decision": "REVIEW"
        },
        {
            "name": "Wire Transfer - Medium Risk",
            "transaction": Transaction(
                transaction_id=f"TXN-{random.randint(100000, 999999)}",
                customer_id="CUST002",
                amount=3200.00,
                currency="USD",
                merchant_id="MERCH-9988",
                mcc_code="4829",  # Wire Transfer
                location="New York",
                timestamp=datetime.now(),
                device_id="DEV99999"
            ),
            "expected_decision": "REVIEW"
        }
    ]
    
    return scenarios


def main():
    print("🚀 Clerivon AI - Database Seeding Script")
    print("=" * 50)
    
    # Initialize pipeline
    pipeline = FraudDetectionPipeline()
    
    # Create sample transactions
    scenarios = create_sample_transactions()
    
    print(f"\n📦 Processing {len(scenarios)} sample transactions...\n")
    
    cases_created = 0
    cases_approved = 0
    cases_blocked = 0
    cases_review = 0
    
    for scenario in scenarios:
        print(f"Processing: {scenario['name']}")
        
        # Process through pipeline
        result = pipeline.process_transaction(scenario['transaction'])
        
        if result['status'] == 'AUTO_APPROVED':
            print(f"  ✅ Auto-approved (risk too low)")
            cases_approved += 1
        else:
            # Save case to database
            case_file = result['case_file']
            db.save_case(case_file)
            cases_created += 1
            
            decision = result['decision']
            if decision == 'BLOCK':
                print(f"  🚫 Case created - Decision: BLOCK (Risk: {case_file['risk_assessment']['total_risk_score']})")
                cases_blocked += 1
            elif decision == 'REVIEW':
                print(f"  ⚠️  Case created - Decision: REVIEW (Risk: {case_file['risk_assessment']['total_risk_score']})")
                cases_review += 1
            else:
                print(f"  ✅ Case created - Decision: APPROVE")
                cases_approved += 1
        
        print()
    
    print("=" * 50)
    print("📊 Seeding Complete!")
    print(f"  - Total transactions processed: {len(scenarios)}")
    print(f"  - Cases created: {cases_created}")
    print(f"  - Auto-approved: {cases_approved}")
    print(f"  - Blocked: {cases_blocked}")
    print(f"  - Needs Review: {cases_review}")
    print()
    
    # Show flywheel metrics
    metrics = db.get_flywheel_metrics()
    print("📈 Current Flywheel Metrics:")
    print(f"  - Total Cases: {metrics['total_cases']}")
    print(f"  - Pending Review: {metrics['pending_cases']}")
    print(f"  - Agreement Rate: {metrics['agreement_rate']}%")
    print()
    
    print("✅ Database seeded successfully!")
    print("\nNext steps:")
    print("  1. Run: streamlit run app.py")
    print("  2. Navigate to 'Case Review' to review pending cases")
    print("  3. Click 'Confirm' or 'Override' to trigger the flywheel")
    print("  4. Check 'Flywheel Analytics' to see learning in action")


if __name__ == "__main__":
    main()
