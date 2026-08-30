"""
Multi-Agent Pipeline for Fraud Detection
5-Agent Architecture: Monitor, Investigator, Adjudicator, Explainer, Feedback
"""

import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

from .tools import (
    get_customer_profile,
    geo_velocity_check,
    get_device_history,
    check_merchant_risk,
    get_transaction_history,
    check_sanctions_list,
    calculate_behavioral_anomaly
)


@dataclass
class Transaction:
    """Represents a financial transaction."""
    transaction_id: str
    customer_id: str
    amount: float
    currency: str
    merchant_id: str
    mcc_code: str
    location: str
    timestamp: datetime
    device_id: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "customer_id": self.customer_id,
            "amount": self.amount,
            "currency": self.currency,
            "merchant_id": self.merchant_id,
            "mcc_code": self.mcc_code,
            "location": self.location,
            "timestamp": self.timestamp.isoformat(),
            "device_id": self.device_id
        }


@dataclass
class AgentResponse:
    """Standard response format for all agents."""
    agent_name: str
    action: str
    reasoning: str
    evidence: Dict[str, Any]
    risk_score_contribution: int
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "action": self.action,
            "reasoning": self.reasoning,
            "evidence": self.evidence,
            "risk_score_contribution": self.risk_score_contribution,
            "timestamp": self.timestamp.isoformat()
        }


class MonitorAgent:
    """
    Agent 1: Monitor Agent
    Continuously scans incoming transactions for initial red flags.
    """
    
    def __init__(self):
        self.name = "Monitor Agent"
        self.threshold = 15  # Lowered threshold for demo escalation
    
    def analyze(self, transaction: Transaction) -> AgentResponse:
        """Perform initial risk assessment."""
        risk_score = 0
        flags = []
        
        # Basic rule-based checks
        if transaction.amount > 5000:
            risk_score += 10
            flags.append(f"High value transaction: ${transaction.amount}")
        
        # Check MCC code risk
        mcc_high_risk = ["7995", "4829", "5944"]
        if transaction.mcc_code in mcc_high_risk:
            risk_score += 8
            flags.append(f"High-risk MCC code: {transaction.mcc_code}")
        
        # Night transaction check
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 23:
            risk_score += 5
            flags.append("Unusual transaction time (night)")
        
        # Unknown device check
        if "DEV99999" in transaction.device_id:
            risk_score += 7
            flags.append("Unknown device detected")
        
        should_escalate = risk_score >= self.threshold
        
        return AgentResponse(
            agent_name=self.name,
            action="ESCALATE" if should_escalate else "APPROVE",
            reasoning=f"Initial risk assessment: {risk_score}/100. Flags: {'; '.join(flags) if flags else 'None'}",
            evidence={"flags": flags, "initial_risk_score": risk_score},
            risk_score_contribution=risk_score,
            timestamp=datetime.now()
        )


class InvestigatorAgent:
    """
    Agent 2: Investigator Agent
    Performs deep-dive investigation using multiple MCP tools.
    """
    
    def __init__(self):
        self.name = "Investigator Agent"
        self.tools_called = []
    
    def analyze(self, transaction: Transaction, monitor_response: AgentResponse) -> AgentResponse:
        """Conduct comprehensive investigation."""
        evidence = {}
        total_risk = 0
        findings = []
        
        # Tool Call 1: Customer Profile
        customer_profile = get_customer_profile(transaction.customer_id)
        evidence["customer_profile"] = customer_profile
        total_risk += customer_profile.get("risk_score", 0) // 5
        findings.append(f"Customer: {customer_profile.get('name', 'Unknown')}")
        self.tools_called.append("get_customer_profile")
        
        # Tool Call 2: Geo Velocity Check
        geo_result = geo_velocity_check(
            transaction.customer_id,
            transaction.location,
            transaction.timestamp
        )
        evidence["geo_velocity"] = geo_result
        total_risk += geo_result.get("risk_contribution", 0)
        if geo_result.get("impossible_travel_detected"):
            findings.append(f"IMPOSSIBLE TRAVEL: {geo_result['last_location']} → {geo_result['current_location']} in {geo_result['time_diff_minutes']} min")
        self.tools_called.append("geo_velocity_check")
        
        # Tool Call 3: Device History
        device_info = get_device_history(transaction.customer_id)
        evidence["device_history"] = device_info
        total_risk += device_info.get("risk_contribution", 0)
        if not device_info.get("is_known_device"):
            findings.append("Unknown device used")
        self.tools_called.append("get_device_history")
        
        # Tool Call 4: Merchant Risk
        merchant_info = check_merchant_risk(transaction.merchant_id, transaction.mcc_code)
        evidence["merchant_risk"] = merchant_info
        total_risk += merchant_info.get("risk_contribution", 0)
        if merchant_info.get("risk_level") == "high":
            findings.append(f"High-risk merchant category: {merchant_info['category']}")
        self.tools_called.append("check_merchant_risk")
        
        # Tool Call 5: Transaction History
        tx_history = get_transaction_history(transaction.customer_id)
        evidence["transaction_history"] = tx_history
        total_risk += tx_history.get("risk_contribution", 0)
        self.tools_called.append("get_transaction_history")
        
        # Tool Call 6: Behavioral Anomaly
        anomaly_result = calculate_behavioral_anomaly(transaction.amount, transaction.customer_id)
        evidence["behavioral_anomaly"] = anomaly_result
        total_risk += anomaly_result.get("risk_contribution", 0)
        if anomaly_result.get("anomaly_detected"):
            findings.append(f"Behavioral anomaly detected (z-score: {anomaly_result['z_score']})")
        self.tools_called.append("calculate_behavioral_anomaly")
        
        return AgentResponse(
            agent_name=self.name,
            action="INVESTIGATE_COMPLETE",
            reasoning=f"Investigation complete. {len(self.tools_called)} tools called. Findings: {'; '.join(findings)}",
            evidence=evidence,
            risk_score_contribution=total_risk,
            timestamp=datetime.now()
        )


class AdjudicatorAgent:
    """
    Agent 3: Adjudicator Agent
    Makes final decision based on all evidence.
    """
    
    def __init__(self):
        self.name = "Adjudicator Agent"
        self.block_threshold = 50
        self.review_threshold = 25
    
    def analyze(self, transaction: Transaction, 
                monitor_response: AgentResponse, 
                investigator_response: AgentResponse) -> AgentResponse:
        """Make final adjudication decision."""
        
        total_risk = (
            monitor_response.risk_score_contribution +
            investigator_response.risk_score_contribution
        )
        
        # Determine action
        if total_risk >= self.block_threshold:
            action = "BLOCK"
            confidence = min(total_risk, 100)
        elif total_risk >= self.review_threshold:
            action = "REVIEW"
            confidence = 70
        else:
            action = "APPROVE"
            confidence = max(100 - total_risk, 50)
        
        # Build reasoning with scoring breakdown
        reasoning = (
            f"Total Risk Score: {total_risk}/100. "
            f"Monitor contribution: {monitor_response.risk_score_contribution}. "
            f"Investigator contribution: {investigator_response.risk_score_contribution}. "
            f"Decision threshold: {self.block_threshold} for BLOCK."
        )
        
        return AgentResponse(
            agent_name=self.name,
            action=action,
            reasoning=reasoning,
            evidence={
                "total_risk_score": total_risk,
                "block_threshold": self.block_threshold,
                "review_threshold": self.review_threshold,
                "confidence": confidence,
                "monitor_score": monitor_response.risk_score_contribution,
                "investigator_score": investigator_response.risk_score_contribution
            },
            risk_score_contribution=0,  # Adjudicator doesn't add risk, just decides
            timestamp=datetime.now()
        )


class ExplainerAgent:
    """
    Agent 4: Explainer Agent
    Generates human-readable case file for analysts.
    """
    
    def __init__(self):
        self.name = "Explainer Agent"
    
    def generate_case_file(self, transaction: Transaction,
                           monitor_response: AgentResponse,
                           investigator_response: AgentResponse,
                           adjudicator_response: AgentResponse) -> Dict[str, Any]:
        """Generate comprehensive case file."""
        
        case_file = {
            "case_id": f"CASE-{transaction.transaction_id}",
            "generated_at": datetime.now().isoformat(),
            "transaction_summary": transaction.to_dict(),
            "final_decision": adjudicator_response.action,
            "risk_assessment": {
                "total_risk_score": adjudicator_response.evidence.get("total_risk_score", 0),
                "risk_breakdown": {
                    "initial_flags": monitor_response.evidence.get("flags", []),
                    "investigation_findings": investigator_response.evidence
                }
            },
            "evidence_trail": {
                "monitor_agent": monitor_response.to_dict(),
                "investigator_agent": investigator_response.to_dict(),
                "adjudicator_agent": adjudicator_response.to_dict()
            },
            "analyst_summary": self._generate_narrative(
                transaction, monitor_response, investigator_response, adjudicator_response
            )
        }
        
        return case_file
    
    def _generate_narrative(self, transaction: Transaction,
                            monitor_response: AgentResponse,
                            investigator_response: AgentResponse,
                            adjudicator_response: AgentResponse) -> str:
        """Generate natural language summary for analysts."""
        
        decision = adjudicator_response.action
        risk_score = adjudicator_response.evidence.get("total_risk_score", 0)
        
        narrative = f"Transaction of ${transaction.amount} at {transaction.location}. "
        narrative += f"Risk score: {risk_score}/100. "
        narrative += f"Recommendation: {decision}. "
        
        if decision == "BLOCK":
            narrative += "Immediate action required due to high fraud indicators."
        elif decision == "REVIEW":
            narrative += "Manual review recommended before final decision."
        else:
            narrative += "No significant fraud indicators detected."
        
        return narrative


class FeedbackAgent:
    """
    Agent 5: Feedback Agent
    Captures human feedback and triggers flywheel learning.
    """
    
    def __init__(self):
        self.name = "Feedback Agent"
        self.feedback_log = []
    
    def capture_feedback(self, case_id: str, human_decision: str, 
                         ai_decision: str, analyst_notes: str = "") -> Dict[str, Any]:
        """Capture and log human feedback."""
        
        feedback_entry = {
            "case_id": case_id,
            "timestamp": datetime.now().isoformat(),
            "ai_decision": ai_decision,
            "human_decision": human_decision,
            "agreement": human_decision == ai_decision,
            "analyst_notes": analyst_notes
        }
        
        self.feedback_log.append(feedback_entry)
        
        # Determine learning action
        if human_decision != ai_decision:
            learning_action = "ADJUST_THRESHOLD"
            if ai_decision == "BLOCK" and human_decision == "APPROVE":
                adjustment = "INCREASE_THRESHOLD"  # Too many false positives
                note = "False positive detected - consider raising block threshold"
            elif ai_decision == "APPROVE" and human_decision == "BLOCK":
                adjustment = "DECREASE_THRESHOLD"  # False negative
                note = "False negative detected - consider lowering block threshold"
            else:
                adjustment = "REVIEW_RULES"
                note = "Decision mismatch requires rule review"
        else:
            learning_action = "REINFORCE"
            adjustment = "NONE"
            note = "AI decision validated by analyst"
        
        return {
            "feedback_captured": True,
            "learning_action": learning_action,
            "adjustment": adjustment,
            "note": note,
            "feedback_entry": feedback_entry
        }


class FraudDetectionPipeline:
    """
    Orchestrates the 5-agent pipeline for fraud detection.
    """
    
    def __init__(self):
        self.monitor = MonitorAgent()
        self.investigator = InvestigatorAgent()
        self.adjudicator = AdjudicatorAgent()
        self.explainer = ExplainerAgent()
        self.feedback = FeedbackAgent()
    
    def process_transaction(self, transaction: Transaction) -> Dict[str, Any]:
        """Run complete 5-agent pipeline on a transaction."""
        
        # Agent 1: Monitor
        monitor_response = self.monitor.analyze(transaction)
        
        # Early exit if no escalation needed
        if monitor_response.action == "APPROVE":
            return {
                "status": "AUTO_APPROVED",
                "transaction_id": transaction.transaction_id,
                "decision": "APPROVE",
                "agent_responses": {
                    "monitor": monitor_response.to_dict()
                }
            }
        
        # Agent 2: Investigator
        investigator_response = self.investigator.analyze(transaction, monitor_response)
        
        # Agent 3: Adjudicator
        adjudicator_response = self.adjudicator.analyze(
            transaction, monitor_response, investigator_response
        )
        
        # Agent 4: Explainer (generates case file)
        case_file = self.explainer.generate_case_file(
            transaction, monitor_response, investigator_response, adjudicator_response
        )
        
        return {
            "status": "CASE_GENERATED",
            "transaction_id": transaction.transaction_id,
            "decision": adjudicator_response.action,
            "case_file": case_file,
            "agent_responses": {
                "monitor": monitor_response.to_dict(),
                "investigator": investigator_response.to_dict(),
                "adjudicator": adjudicator_response.to_dict()
            }
        }
    
    def submit_feedback(self, case_id: str, human_decision: str, 
                       ai_decision: str, analyst_notes: str = "") -> Dict[str, Any]:
        """Submit human feedback for learning."""
        return self.feedback.capture_feedback(
            case_id, human_decision, ai_decision, analyst_notes
        )
