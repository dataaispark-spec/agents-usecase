"""
Streamlit UI — BFSI Agents Fraud Lab (Clerivon AI) v1.1.1
Synthetic multi-agent demo: Live Feed → Case Review → Flywheel
Repo: https://github.com/dataaispark-spec/bfsi-agents-fraud-lab
"""

from __future__ import annotations

import json
import os
import random
import sys
from datetime import datetime

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fraud_agents.agents import FraudDetectionPipeline, Transaction
from fraud_agents.db_factory import db as get_db

APP_VERSION = os.getenv("APP_VERSION", "1.1.1")
DB_BACKEND = os.getenv("DB_BACKEND", "sqlite")

st.set_page_config(
    page_title="BFSI Agents Fraud Lab",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1a1a2e; }
    .case-card {
        background-color: #f8f9fa; border-left: 4px solid #667eea;
        border-radius: 5px; padding: 1rem; margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)


def generate_synthetic_transaction(scenario: str = "normal") -> Transaction:
    scenarios = {
        "impossible_travel": {
            "customer_id": "CUST001",
            "amount": 4500.00,
            "location": "Singapore",
            "mcc_code": "5944",
            "device_id": "DEV99999",
        },
        "high_value_gambling": {
            "customer_id": "CUST002",
            "amount": 8500.00,
            "location": "Tokyo",
            "mcc_code": "7995",
            "device_id": "DEV99999",
        },
        "normal_transaction": {
            "customer_id": "CUST003",
            "amount": 185.50,
            "location": "Singapore",
            "mcc_code": "5411",
            "device_id": "DEV67890",
        },
        "anomaly_detection": {
            "customer_id": "CUST001",
            "amount": 2500.00,
            "location": "London",
            "mcc_code": "5812",
            "device_id": "DEV12345",
        },
    }
    config = scenarios.get(scenario, scenarios["normal_transaction"])
    return Transaction(
        transaction_id=f"TXN-{random.randint(100000, 999999)}",
        customer_id=config["customer_id"],
        amount=config["amount"],
        currency="USD",
        merchant_id=f"MERCH-{random.randint(1000, 9999)}",
        mcc_code=config["mcc_code"],
        location=config["location"],
        timestamp=datetime.now(),
        device_id=config["device_id"],
    )


def main():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = FraudDetectionPipeline()
    if "cases" not in st.session_state:
        st.session_state.cases = []

    database = get_db()

    st.sidebar.title("BFSI Agents Lab")
    st.sidebar.caption(f"Fraud lab **v{APP_VERSION}** · DB: `{DB_BACKEND}`")
    menu = ["Live Feed", "Case Review", "Flywheel Analytics", "Settings"]
    choice = st.sidebar.selectbox("Menu", menu)
    st.sidebar.info("Synthetic tools only. Not connected to live banking systems.")

    if choice == "Live Feed":
        live_feed_page(database)
    elif choice == "Case Review":
        case_review_page(database)
    elif choice == "Flywheel Analytics":
        flywheel_page(database)
    else:
        settings_page(database)


def live_feed_page(database):
    st.markdown('<p class="main-header">Live Transaction Feed</p>', unsafe_allow_html=True)
    st.markdown("Demo fraud detection — 5-agent pipeline (synthetic BFSI data)")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        scenario = st.selectbox(
            "Transaction Scenario",
            [
                "impossible_travel",
                "high_value_gambling",
                "normal_transaction",
                "anomaly_detection",
            ],
            index=0,
        )
    with col2:
        auto_process = st.checkbox("Auto-process after generation", value=True)
    with col3:
        generate_btn = st.button("Generate Transaction", type="primary", use_container_width=True)

    if not generate_btn:
        return

    with st.spinner("Generating synthetic transaction..."):
        transaction = generate_synthetic_transaction(scenario)
        st.markdown("### Transaction Details")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Transaction ID", transaction.transaction_id)
        c2.metric("Amount", f"${transaction.amount:,.2f}")
        c3.metric("Location", transaction.location)
        c4.metric("MCC", transaction.mcc_code)
        st.json(transaction.to_dict())

        if not auto_process:
            return

        st.markdown("### Agent Pipeline")
        progress = st.progress(0)
        status = st.empty()

        status.text("Monitor Agent...")
        monitor_response = st.session_state.pipeline.monitor.analyze(transaction)
        progress.progress(25)
        with st.expander("Monitor Agent", expanded=True):
            st.write(monitor_response.action, monitor_response.risk_score_contribution)
            st.code(monitor_response.reasoning)

        if monitor_response.action == "APPROVE":
            st.success("Auto-approved — no case created.")
            progress.progress(100)
            return

        status.text("Investigator Agent...")
        inv = st.session_state.pipeline.investigator.analyze(transaction, monitor_response)
        progress.progress(50)
        with st.expander("Investigator Agent", expanded=True):
            geo = inv.evidence.get("geo_velocity", {})
            if geo.get("impossible_travel_detected"):
                st.error(
                    f"Impossible travel: {geo.get('last_location')} → {geo.get('current_location')}"
                )
            st.json(inv.evidence)

        status.text("Adjudicator Agent...")
        adj = st.session_state.pipeline.adjudicator.analyze(transaction, monitor_response, inv)
        progress.progress(75)
        with st.expander("Adjudicator", expanded=True):
            st.write(adj.action)
            st.code(adj.reasoning)

        status.text("Explainer / save case...")
        case_file = st.session_state.pipeline.explainer.generate_case_file(
            transaction, monitor_response, inv, adj
        )
        ok = database.save_case(case_file)
        st.session_state.cases.append(case_file)
        progress.progress(100)
        if ok:
            st.success(f"Case saved: {case_file['case_id']}")
        else:
            st.error("Failed to persist case — check DB logs.")
        st.info(case_file.get("analyst_summary", ""))
        with st.expander("Full case JSON"):
            st.json(case_file)


def case_review_page(database):
    st.markdown('<p class="main-header">Case Review Queue</p>', unsafe_allow_html=True)
    pending = database.get_pending_cases()
    if not pending:
        st.info("No pending cases. Generate transactions on Live Feed.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Pending", len(pending))
    c2.metric("High risk", sum(1 for c in pending if (c.get("risk_score") or 0) > 50))
    c3.metric("Medium", sum(1 for c in pending if 25 <= (c.get("risk_score") or 0) <= 50))

    for case in pending:
        st.markdown(
            f"**{case['case_id']}** · ${case.get('amount') or 0:,.2f} · "
            f"{case.get('location')} · risk {case.get('risk_score')} · AI: {case.get('ai_decision')}"
        )
        with st.expander("Details & decision"):
            details = database.get_case_details(case["case_id"])
            if details:
                for response in details.get("agent_responses", []):
                    st.markdown(f"**{response.get('agent_name')}**")
                    st.code(response.get("reasoning") or "")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Confirm AI", key=f"c_{case['case_id']}"):
                    database.update_human_decision(case["case_id"], case["ai_decision"])
                    fb = st.session_state.pipeline.submit_feedback(
                        case["case_id"],
                        case["ai_decision"],
                        case["ai_decision"],
                        "Analyst confirmed",
                    )
                    database.save_feedback(case["case_id"], fb)
                    st.success("Recorded")
                    st.rerun()
            with col2:
                override = "APPROVE" if case.get("ai_decision") != "APPROVE" else "BLOCK"
                if st.button(f"Override → {override}", key=f"o_{case['case_id']}"):
                    database.update_human_decision(case["case_id"], override)
                    fb = st.session_state.pipeline.submit_feedback(
                        case["case_id"],
                        override,
                        case["ai_decision"],
                        f"Override to {override}",
                    )
                    database.save_feedback(case["case_id"], fb)
                    st.warning("Override recorded")
                    st.rerun()
            with col3:
                if st.button("Escalate", key=f"e_{case['case_id']}"):
                    st.info("Escalation noted (lab: no external queue).")


def flywheel_page(database):
    st.markdown('<p class="main-header">Flywheel Analytics</p>', unsafe_allow_html=True)
    metrics = database.get_flywheel_metrics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total cases", metrics["total_cases"])
    c2.metric("Agreement %", f"{metrics['agreement_rate']}%")
    c3.metric("False positives", metrics["false_positives"])
    c4.metric("False negatives", metrics["false_negatives"])
    recent = database.get_recent_feedback(20)
    if recent:
        st.dataframe(recent, use_container_width=True)
    else:
        st.info("No feedback yet — review cases first.")


def settings_page(database):
    st.markdown('<p class="main-header">Settings</p>', unsafe_allow_html=True)
    st.write(
        f"**Repo:** dataaispark-spec/bfsi-agents-fraud-lab  \n"
        f"**Version:** {APP_VERSION}  \n"
        f"**DB backend:** `{DB_BACKEND}`  \n"
        f"**Mode:** Lab / Pilot (synthetic tools)"
    )
    st.markdown(
        """
### Pipeline
- Monitor → Investigator (synthetic tools) → Adjudicator → Explainer → Feedback

### Not in this lab build
- Live core-banking / device / sanctions APIs
- Production SSO (stubs only in `fraud_agents/auth.py`)
- Bank-grade latency SLAs

See **SETUP_LAB.md** for deploy options.
"""
    )
    metrics = database.get_flywheel_metrics()
    st.json(metrics)


if __name__ == "__main__":
    main()
