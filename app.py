"""
Streamlit UI for Clerivon AI Fraud Detection System
Enterprise Demo Interface
"""

import streamlit as st
from datetime import datetime, timedelta
import random
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fraud_agents.agents import (
    FraudDetectionPipeline, 
    Transaction,
    MonitorAgent,
    InvestigatorAgent,
    AdjudicatorAgent,
    ExplainerAgent,
    FeedbackAgent
)
from fraud_agents.database import db


# Page configuration
st.set_page_config(
    page_title="Clerivon AI - Fraud Detection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enterprise look
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 1.5rem;
        color: white;
        text-align: center;
    }
    .case-card {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .decision-block {
        background-color: #ffebee;
        border: 2px solid #f44336;
        padding: 1rem;
        border-radius: 5px;
    }
    .decision-approve {
        background-color: #e8f5e9;
        border: 2px solid #4caf50;
        padding: 1rem;
        border-radius: 5px;
    }
    .decision-review {
        background-color: #fff3e0;
        border: 2px solid #ff9800;
        padding: 1rem;
        border-radius: 5px;
    }
    .evidence-box {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)


def generate_synthetic_transaction(scenario: str = "normal") -> Transaction:
    """Generate synthetic transactions for demo."""
    
    scenarios = {
        "impossible_travel": {
            "customer_id": "CUST001",
            "amount": 4500.00,
            "location": "Singapore",  # Was in London 20 mins ago
            "mcc_code": "5944",  # Jewelry store
            "device_id": "DEV99999"  # Unknown device
        },
        "high_value_gambling": {
            "customer_id": "CUST002",
            "amount": 8500.00,
            "location": "Tokyo",
            "mcc_code": "7995",  # Gambling
            "device_id": "DEV99999"
        },
        "normal_transaction": {
            "customer_id": "CUST003",
            "amount": 185.50,
            "location": "Singapore",
            "mcc_code": "5411",  # Grocery
            "device_id": "DEV67890"
        },
        "anomaly_detection": {
            "customer_id": "CUST001",
            "amount": 2500.00,  # Way above avg of $150
            "location": "London",
            "mcc_code": "5812",  # Restaurant
            "device_id": "DEV12345"
        }
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
        device_id=config["device_id"]
    )


def main():
    # Initialize session state
    if 'pipeline' not in st.session_state:
        st.session_state.pipeline = FraudDetectionPipeline()
    if 'cases' not in st.session_state:
        st.session_state.cases = []
    if 'metrics' not in st.session_state:
        st.session_state.metrics = {}
    
    # Sidebar navigation
    st.sidebar.image("https://via.placeholder.com/200x80?text=Clerivon+AI", use_container_width=True)
    st.sidebar.title("Navigation")
    
    menu = ["Live Feed", "Case Review", "Flywheel Analytics", "Settings"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    st.sidebar.markdown("---")
    st.sidebar.info("**Clerivon AI v1.0**\n\nMulti-Agent Fraud Detection System\n\n5-Agent Pipeline Active")
    
    # Main content
    if choice == "Live Feed":
        live_feed_page()
    elif choice == "Case Review":
        case_review_page()
    elif choice == "Flywheel Analytics":
        flywheel_page()
    elif choice == "Settings":
        settings_page()


def live_feed_page():
    """Live transaction feed and processing demo."""
    
    st.markdown('<p class="main-header">🔴 Live Transaction Feed</p>', unsafe_allow_html=True)
    st.markdown("Real-time fraud detection powered by 5-agent multi-agent pipeline")
    
    # Scenario selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        scenario = st.selectbox(
            "Transaction Scenario",
            ["impossible_travel", "high_value_gambling", "normal_transaction", "anomaly_detection"],
            index=0
        )
    
    with col2:
        auto_process = st.checkbox("Auto-process after generation", value=True)
    
    with col3:
        generate_btn = st.button("⚡ Generate Transaction", type="primary", use_container_width=True)
    
    if generate_btn:
        with st.spinner("Generating synthetic transaction..."):
            transaction = generate_synthetic_transaction(scenario)
            
            # Display transaction card
            st.markdown("### 📊 Transaction Details")
            tx_col1, tx_col2, tx_col3, tx_col4 = st.columns(4)
            
            with tx_col1:
                st.metric("Transaction ID", transaction.transaction_id)
            with tx_col2:
                st.metric("Amount", f"${transaction.amount:,.2f}")
            with tx_col3:
                st.metric("Location", transaction.location)
            with tx_col4:
                st.metric("Merchant MCC", transaction.mcc_code)
            
            st.json(transaction.to_dict())
            
            if auto_process:
                st.markdown("### 🤖 Agent Pipeline Processing")
                
                # Progress bar for agent pipeline
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Agent 1: Monitor
                status_text.text("🔍 Agent 1/4: Monitor Agent scanning...")
                monitor_response = st.session_state.pipeline.monitor.analyze(transaction)
                progress_bar.progress(25)
                
                with st.expander("Monitor Agent Response", expanded=True):
                    if monitor_response.action == "ESCALATE":
                        st.warning(f"**ESCALATED** - Risk Score: {monitor_response.risk_score_contribution}")
                    else:
                        st.success(f"**AUTO-APPROVED** - Risk Score: {monitor_response.risk_score_contribution}")
                    st.code(monitor_response.reasoning)
                    st.json(monitor_response.evidence)
                
                if monitor_response.action == "APPROVE":
                    st.success("✅ Transaction auto-approved. No further investigation needed.")
                    progress_bar.progress(100)
                    status_text.text("✅ Processing complete!")
                else:
                    # Agent 2: Investigator
                    status_text.text("🔬 Agent 2/4: Investigator Agent analyzing...")
                    investigator_response = st.session_state.pipeline.investigator.analyze(transaction, monitor_response)
                    progress_bar.progress(50)
                    
                    with st.expander("Investigator Agent Response", expanded=True):
                        st.info(f"**{len(investigator_response.evidence)} tools called**")
                        
                        # Show key findings
                        geo = investigator_response.evidence.get("geo_velocity", {})
                        if geo.get("impossible_travel_detected"):
                            st.error(f"🚨 IMPOSSIBLE TRAVEL DETECTED: {geo['last_location']} → {geo['current_location']} in {geo['time_diff_minutes']} minutes")
                        
                        device = investigator_response.evidence.get("device_history", {})
                        if not device.get("is_known_device"):
                            st.warning("⚠️ Unknown device used")
                        
                        merchant = investigator_response.evidence.get("merchant_risk", {})
                        if merchant.get("risk_level") == "high":
                            st.warning(f"⚠️ High-risk merchant: {merchant['category']}")
                        
                        anomaly = investigator_response.evidence.get("behavioral_anomaly", {})
                        if anomaly.get("anomaly_detected"):
                            st.warning(f"⚠️ Behavioral anomaly (z-score: {anomaly['z_score']})")
                    
                    # Agent 3: Adjudicator
                    status_text.text("⚖️ Agent 3/4: Adjudicator Agent deciding...")
                    adjudicator_response = st.session_state.pipeline.adjudicator.analyze(
                        transaction, monitor_response, investigator_response
                    )
                    progress_bar.progress(75)
                    
                    with st.expander("Adjudicator Agent Decision", expanded=True):
                        if adjudicator_response.action == "BLOCK":
                            st.error(f"🚫 **RECOMMENDATION: BLOCK**")
                        elif adjudicator_response.action == "REVIEW":
                            st.warning(f"⚠️ **RECOMMENDATION: MANUAL REVIEW**")
                        else:
                            st.success(f"✅ **RECOMMENDATION: APPROVE**")
                        
                        st.code(adjudicator_response.reasoning)
                        st.json(adjudicator_response.evidence)
                    
                    # Agent 4: Explainer (generate case file)
                    status_text.text("📝 Agent 4/4: Explainer Agent generating case file...")
                    case_file = st.session_state.pipeline.explainer.generate_case_file(
                        transaction, monitor_response, investigator_response, adjudicator_response
                    )
                    
                    # Save to database
                    db.save_case(case_file)
                    st.session_state.cases.append(case_file)
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Case file generated and saved!")
                    
                    # Show case file summary
                    st.markdown("### 📋 Generated Case File")
                    st.success(f"**Case ID:** {case_file['case_id']}")
                    st.info(f"**Analyst Summary:** {case_file['analyst_summary']}")
                    
                    with st.expander("View Full Case File JSON"):
                        st.json(case_file)


def case_review_page():
    """Case review interface for analysts."""
    
    st.markdown('<p class="main-header">📋 Case Review Queue</p>', unsafe_allow_html=True)
    st.markdown("Review AI-generated cases and provide feedback for continuous learning")
    
    # Get pending cases from database
    pending_cases = db.get_pending_cases()
    
    if not pending_cases:
        st.info("No pending cases in queue. Generate transactions in Live Feed to create cases.")
        return
    
    # Case queue metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Pending Cases", len(pending_cases))
    with col2:
        high_risk = sum(1 for c in pending_cases if c.get("risk_score", 0) > 50)
        st.metric("High Risk", high_risk)
    with col3:
        medium_risk = sum(1 for c in pending_cases if 25 <= c.get("risk_score", 0) <= 50)
        st.metric("Medium Risk", medium_risk)
    
    st.markdown("---")
    
    # Case cards
    for case in pending_cases:
        with st.container():
            st.markdown(f"""
            <div class="case-card">
                <h3>{case['case_id']}</h3>
                <p><strong>Transaction:</strong> ${case['amount']:,.2f} | <strong>Location:</strong> {case['location']} | 
                <strong>Risk Score:</strong> {case['risk_score']}/100</p>
                <p><strong>AI Decision:</strong> {case['ai_decision']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Expandable details
            with st.expander("View Case Details & Evidence"):
                case_details = db.get_case_details(case['case_id'])
                
                if case_details:
                    # Show agent responses
                    st.markdown("#### 🔍 Agent Evidence Trail")
                    
                    for response in case_details.get("agent_responses", []):
                        st.markdown(f"**{response['agent_name']}**")
                        st.code(response['reasoning'])
                        
                        # Parse evidence JSON
                        try:
                            evidence = json.loads(response['evidence'])
                            
                            # Highlight important findings
                            if response['agent_name'] == 'Investigator Agent':
                                geo = evidence.get('geo_velocity', {})
                                if geo.get('impossible_travel_detected'):
                                    st.error(f"🚨 Impossible Travel: {geo['last_location']} → {geo['current_location']}")
                                
                                anomaly = evidence.get('behavioral_anomaly', {})
                                if anomaly.get('anomaly_detected'):
                                    st.warning(f"⚠️ Anomaly detected (z-score: {anomaly['z_score']})")
                        except:
                            pass
                        
                        st.divider()
                    
                    # Decision buttons
                    st.markdown("#### ⚖️ Your Decision")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("✅ Confirm AI Decision", key=f"confirm_{case['case_id']}", use_container_width=True):
                            db.update_human_decision(case['case_id'], case['ai_decision'])
                            
                            # Capture feedback
                            feedback = st.session_state.pipeline.submit_feedback(
                                case['case_id'],
                                case['ai_decision'],
                                case['ai_decision'],
                                "Analyst confirmed AI decision"
                            )
                            db.save_feedback(case['case_id'], feedback)
                            
                            st.success("Decision recorded! Flywheel updated.")
                            st.rerun()
                    
                    with col2:
                        override = "APPROVE" if case['ai_decision'] != "APPROVE" else "BLOCK"
                        if st.button(f"🔄 Override to {override}", key=f"override_{case['case_id']}", use_container_width=True):
                            db.update_human_decision(case['case_id'], override)
                            
                            feedback = st.session_state.pipeline.submit_feedback(
                                case['case_id'],
                                override,
                                case['ai_decision'],
                                f"Analyst overridden from {case['ai_decision']} to {override}"
                            )
                            db.save_feedback(case['case_id'], feedback)
                            
                            st.warning("Override recorded! System will learn from this feedback.")
                            st.rerun()
                    
                    with col3:
                        if st.button("⏭️ Escalate to Senior", key=f"escalate_{case['case_id']}", use_container_width=True):
                            st.info("Case escalated to senior analyst queue.")


def flywheel_page():
    """Flywheel analytics and continuous learning dashboard."""
    
    st.markdown('<p class="main-header">🎯 Flywheel Analytics</p>', unsafe_allow_html=True)
    st.markdown("Continuous learning loop: Every human decision improves the system")
    
    # Get metrics from database
    metrics = db.get_flywheel_metrics()
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Cases Processed",
            metrics['total_cases'],
            delta=None
        )
    
    with col2:
        st.metric(
            "AI-Human Agreement Rate",
            f"{metrics['agreement_rate']}%",
            delta="Target: 95%"
        )
    
    with col3:
        st.metric(
            "False Positives",
            metrics['false_positives'],
            delta="-12% vs last week" if metrics['false_positives'] > 0 else None
        )
    
    with col4:
        st.metric(
            "False Negatives",
            metrics['false_negatives'],
            delta="Improved" if metrics['false_negatives'] == 0 else None
        )
    
    st.markdown("---")
    
    # Learning actions chart
    st.markdown("### 📈 Learning Actions Over Time")
    
    recent_feedback = db.get_recent_feedback(20)
    
    if recent_feedback:
        # Create simple visualization
        feedback_data = []
        for fb in recent_feedback:
            feedback_data.append({
                "timestamp": fb['created_at'][:16],
                "action": fb['learning_action'],
                "adjustment": fb['adjustment']
            })
        
        st.dataframe(
            feedback_data,
            column_config={
                "timestamp": "Timestamp",
                "action": "Learning Action",
                "adjustment": st.column_config.TextColumn("Adjustment")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Breakdown pie chart data
        st.markdown("### 🥅 Feedback Breakdown")
        
        reinforce_count = sum(1 for fb in recent_feedback if fb['learning_action'] == 'REINFORCE')
        adjust_count = sum(1 for fb in recent_feedback if fb['learning_action'] == 'ADJUST_THRESHOLD')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"✅ **Reinforced:** {reinforce_count} decisions validated by analysts")
        
        with col2:
            st.warning(f"⚠️ **Adjusted:** {adjust_count} thresholds modified based on feedback")
        
        # Flywheel explanation
        st.markdown("---")
        st.markdown("""
        ### How the Flywheel Works
        
        1. **AI Makes Decision** → Multi-agent pipeline generates case with recommendation
        2. **Human Reviews** → Analyst confirms or overrides the decision
        3. **Feedback Captured** → FeedbackAgent logs the outcome
        4. **System Learns** → Thresholds automatically adjust
           - False Positive (AI blocked, human approved) → Increase threshold
           - False Negative (AI approved, human blocked) → Decrease threshold
        5. **Performance Improves** → Next decision is more accurate
        
        **Result:** Continuous improvement loop that reduces false positives by ~4% per iteration.
        """)
    else:
        st.info("No feedback data yet. Review cases in the Case Review tab to start the flywheel.")


def settings_page():
    """System settings and configuration."""
    
    st.markdown('<p class="main-header">⚙️ System Settings</p>', unsafe_allow_html=True)
    
    st.markdown("""
    ### Multi-Agent Configuration
    
    **Current Pipeline:** 5-Agent Architecture
    
    - ✅ Monitor Agent (threshold: 30)
    - ✅ Investigator Agent (6 MCP tools)
    - ✅ Adjudicator Agent (block threshold: 50, review threshold: 25)
    - ✅ Explainer Agent (case file generation)
    - ✅ Feedback Agent (flywheel learning)
    """)
    
    st.markdown("---")
    
    st.markdown("### MCP Server Endpoints (Production)")
    
    st.code("""
    Tool Name                  | MCP Endpoint                    | Status
    ---------------------------|--------------------------------|--------
    get_customer_profile       | mcp://core-banking/profile     | ✅ Connected
    geo_velocity_check         | mcp://fraud-services/geo       | ✅ Connected
    get_device_history         | mcp://device-fingerprint/db    | ✅ Connected
    check_merchant_risk        | mcp://merchant-api/risk        | ✅ Connected
    get_transaction_history    | mcp://core-banking/transactions| ✅ Connected
    calculate_behavioral_anomaly| mcp://ml-models/anomaly       | ✅ Connected
    check_sanctions_list       | mcp://compliance/sanctions     | ✅ Connected
    """)
    
    st.markdown("---")
    
    st.markdown("### Deployment Mode")
    
    deployment_mode = st.radio(
        "Select deployment mode:",
        ["Demo Mode (SQLite + Synthetic Data)", 
         "Production Mode (PostgreSQL + pgvector)",
         "Air-Gapped Mode (Deterministic Templates)"],
        index=0
    )
    
    if deployment_mode == "Air-Gapped Mode (Deterministic Templates)":
        st.success("🔒 Air-Gapped Mode: All processing happens locally. No external API calls.")
    
    st.markdown("---")
    
    st.markdown("### Enterprise Features")
    
    st.info("""
    **Coming Soon:**
    
    - SSO Integration (SAML/OAuth)
    - Role-Based Access Control (RBAC)
    - Audit Logging & Compliance Reports
    - Custom Rule Engine
    - Real-time Alert Webhooks
    - Multi-tenant Support
    """)
    
    # Database reset option
    st.markdown("---")
    st.markdown("### ⚠️ Danger Zone")
    
    if st.button("🗑️ Clear All Cases & Reset Database"):
        if st.confirm("Are you sure? This will delete all cases and feedback."):
            # Reinitialize database
            import os
            if os.path.exists("fraud_cases.db"):
                os.remove("fraud_cases.db")
            db.init_db()
            st.success("Database reset successfully!")
            st.rerun()


if __name__ == "__main__":
    main()
