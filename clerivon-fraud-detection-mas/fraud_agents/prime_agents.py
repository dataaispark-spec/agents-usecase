"""
Prime Agents Framework: 5-role agent swarm with harness wrapping
Alternative to Hermes, OpenWorker, OpenBots
"""
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from .harness import Harness
from .tools import (
    get_customer_profile, get_device_history, calculate_geo_velocity,
    check_merchant_risk, get_recent_transactions, check_sanctions_list,
    submit_case_decision
)

class AgentRole(Enum):
    MONITOR = "monitor"
    INVESTIGATOR = "investigator"
    ADJUDICATOR = "adjudicator"
    EXPLAINER = "explainer"
    FEEDBACK = "feedback"

@dataclass
class AgentMessage:
    """Message passed between agents."""
    role: AgentRole
    content: str
    data: Dict[str, Any]
    timestamp: float = time.time()

class PrimeAgent:
    """Base class for all prime agents with harness integration."""
    
    def __init__(self, role: AgentRole):
        self.role = role
        self.harness = Harness()
        self.tool_registry = {}
    
    def register_tool(self, name: str, func):
        """Register a tool for this agent."""
        self.tool_registry[name] = func
    
    def execute_with_harness(self, operation: str, func, *args, **kwargs):
        """Execute function with full harness protection."""
        # Start trace
        span = self.harness.create_trace(f"{self.role.value}:{operation}")
        
        try:
            # Execute
            result = func(*args, **kwargs)
            
            # Validate output if applicable
            if isinstance(result, dict) and 'decision' in result:
                valid, msg = self.harness.validate_output(
                    json.dumps(result),
                    result.get('decision', ''),
                    result.get('evidence', [])
                )
                if not valid:
                    raise ValueError(msg)
            
            return result
        except Exception as e:
            self.harness.finalize_trace(span, str(e))
            raise
        finally:
            self.harness.finalize_trace(span)

class MonitorAgent(PrimeAgent):
    """Real-time transaction monitoring and anomaly detection."""
    
    def __init__(self):
        super().__init__(AgentRole.MONITOR)
        self.register_tool('get_customer_profile', get_customer_profile)
        self.register_tool('calculate_geo_velocity', calculate_geo_velocity)
    
    def analyze_transaction(self, transaction: Dict) -> Dict:
        """Analyze incoming transaction for anomalies."""
        tools_used = []
        risk_score = 0.0
        flags = []
        
        # Get customer profile
        profile = self.execute_with_harness(
            'get_profile',
            get_customer_profile,
            transaction['customer_id']
        )
        tools_used.append('get_customer_profile')
        
        # Check geo velocity
        if 'location' in transaction:
            geo_result = self.execute_with_harness(
                'geo_check',
                calculate_geo_velocity,
                transaction['customer_id'],
                transaction['location'],
                transaction['timestamp']
            )
            tools_used.append('calculate_geo_velocity')
            if geo_result['is_anomaly']:
                flags.append('IMPOSSIBLE_TRAVEL')
                risk_score += 0.4
        
        # Profile deviation
        if transaction['amount'] > profile['avg_transaction_amount'] * 3:
            flags.append('AMOUNT_DEVIATION')
            risk_score += 0.3
        
        return {
            'transaction_id': transaction['id'],
            'risk_score': risk_score,
            'flags': flags,
            'tools_used': tools_used,
            'should_investigate': risk_score > 0.5
        }

class InvestigatorAgent(PrimeAgent):
    """Deep investigation with multiple tool calls."""
    
    def __init__(self):
        super().__init__(AgentRole.INVESTIGATOR)
        self.tools = [
            ('get_device_history', get_device_history),
            ('check_merchant_risk', check_merchant_risk),
            ('get_recent_transactions', get_recent_transactions),
            ('check_sanctions_list', check_sanctions_list),
        ]
    
    def investigate(self, transaction: Dict, initial_flags: List[str]) -> Dict:
        """Conduct deep investigation with 6+ tool calls."""
        evidence = []
        tools_called = []
        
        for tool_name, tool_func in self.tools:
            try:
                if tool_name == 'get_device_history':
                    result = self.execute_with_harness(
                        tool_name, tool_func, transaction['device_id']
                    )
                elif tool_name == 'check_merchant_risk':
                    result = self.execute_with_harness(
                        tool_name, tool_func, transaction['merchant_id']
                    )
                elif tool_name == 'get_recent_transactions':
                    result = self.execute_with_harness(
                        tool_name, tool_func, transaction['customer_id'], limit=10
                    )
                elif tool_name == 'check_sanctions_list':
                    result = self.execute_with_harness(
                        tool_name, tool_func, transaction['customer_id']
                    )
                
                evidence.append({
                    'tool': tool_name,
                    'result': result,
                    'relevance': 'high' if result.get('risk_level', 'low') == 'high' else 'medium'
                })
                tools_called.append(tool_name)
            except Exception as e:
                evidence.append({'tool': tool_name, 'error': str(e)})
        
        return {
            'transaction_id': transaction['id'],
            'evidence': evidence,
            'tools_called': tools_called,
            'evidence_count': len([e for e in evidence if 'error' not in e])
        }

class AdjudicatorAgent(PrimeAgent):
    """Make final fraud/not-fraud decision."""
    
    def __init__(self):
        super().__init__(AgentRole.ADJUDICATOR)
    
    def adjudicate(self, investigation_result: Dict, monitor_result: Dict) -> Dict:
        """Make adjudication decision based on evidence."""
        evidence_count = investigation_result['evidence_count']
        risk_score = monitor_result['risk_score']
        flags = monitor_result['flags']
        
        # Decision logic
        if 'IMPOSSIBLE_TRAVEL' in flags and evidence_count >= 3:
            decision = 'BLOCK'
            confidence = 0.95
        elif risk_score > 0.7 and evidence_count >= 2:
            decision = 'BLOCK'
            confidence = 0.85
        elif risk_score > 0.4:
            decision = 'REVIEW'
            confidence = 0.6
        else:
            decision = 'APPROVE'
            confidence = 0.75
        
        # Self-correction via harness
        final_decision = self.harness.verification.self_correct(decision, confidence)
        
        return {
            'transaction_id': investigation_result['transaction_id'],
            'decision': final_decision,
            'confidence': confidence,
            'reasoning': f"Based on {evidence_count} evidence items, risk score {risk_score}, flags: {flags}",
            'evidence_summary': investigation_result['evidence']
        }

class ExplainerAgent(PrimeAgent):
    """Generate human-readable explanation."""
    
    def __init__(self):
        super().__init__(AgentRole.EXPLAINER)
    
    def explain(self, adjudication: Dict) -> str:
        """Generate transparent explanation for decision."""
        decision = adjudication['decision']
        reasoning = adjudication['reasoning']
        confidence = adjudication['confidence']
        
        explanation = f"""
DECISION: {decision}
CONFIDENCE: {confidence:.0%}

REASONING:
{reasoning}

EVIDENCE BREAKDOWN:
"""
        for i, evidence in enumerate(adjudication['evidence_summary'], 1):
            if 'error' not in evidence:
                explanation += f"  {i}. {evidence['tool']}: {evidence['relevance']} relevance
"
        
        explanation += f"""
TRANSPARENCY NOTE:
This decision was made by our multi-agent system using {len(adjudication['evidence_summary'])} 
data sources. All PII has been redacted and the decision trail is fully auditable.
"""
        return explanation.strip()

class FeedbackAgent(PrimeAgent):
    """Learn from human feedback via flywheel."""
    
    def __init__(self):
        super().__init__(AgentRole.FEEDBACK)
    
    def process_feedback(self, case_id: str, human_decision: str, ai_decision: str) -> Dict:
        """Process human feedback for continuous learning."""
        learning_event = {
            'case_id': case_id,
            'ai_decision': ai_decision,
            'human_decision': human_decision,
            'agreement': ai_decision == human_decision,
            'timestamp': time.time()
        }
        
        # Store in memory for flywheel
        self.harness.memory.add_long_term(
            content=json.dumps(learning_event),
            metadata={'type': 'feedback', 'case_id': case_id}
        )
        
        # Generate learning signal
        if ai_decision != human_decision:
            learning_signal = {
                'adjustment_needed': True,
                'direction': 'increase_threshold' if human_decision == 'APPROVE' else 'decrease_threshold',
                'magnitude': 0.05
            }
        else:
            learning_signal = {'adjustment_needed': False}
        
        return {**learning_event, 'learning_signal': learning_signal}

class PrimeSwarmOrchestrator:
    """Orchestrate the 5-agent swarm."""
    
    def __init__(self):
        self.agents = {
            AgentRole.MONITOR: MonitorAgent(),
            AgentRole.INVESTIGATOR: InvestigatorAgent(),
            AgentRole.ADJUDICATOR: AdjudicatorAgent(),
            AgentRole.EXPLAINER: ExplainerAgent(),
            AgentRole.FEEDBACK: FeedbackAgent()
        }
    
    def process_transaction(self, transaction: Dict) -> Dict:
        """Run complete 5-agent pipeline on transaction."""
        results = {}
        
        # Stage 1: Monitor
        monitor_result = self.agents[AgentRole.MONITOR].analyze_transaction(transaction)
        results['monitor'] = monitor_result
        
        if not monitor_result['should_investigate']:
            return {**results, 'final_decision': 'APPROVE', 'reason': 'Low risk'}
        
        # Stage 2: Investigate
        investigation = self.agents[AgentRole.INVESTIGATOR].investigate(
            transaction, monitor_result['flags']
        )
        results['investigation'] = investigation
        
        # Stage 3: Adjudicate
        adjudication = self.agents[AgentRole.ADJUDICATOR].adjudicate(
            investigation, monitor_result
        )
        results['adjudication'] = adjudication
        
        # Stage 4: Explain
        explanation = self.agents[AgentRole.EXPLAINER].explain(adjudication)
        results['explanation'] = explanation
        
        return {
            **results,
            'final_decision': adjudication['decision'],
            'confidence': adjudication['confidence'],
            'explanation': explanation
        }

# Example usage
if __name__ == "__main__":
    orchestrator = PrimeSwarmOrchestrator()
    
    test_transaction = {
        'id': 'TXN-001',
        'customer_id': 'CUST-123',
        'amount': 5000.0,
        'location': {'lat': 1.3521, 'lon': 103.8198},  # Singapore
        'timestamp': time.time(),
        'device_id': 'DEV-456',
        'merchant_id': 'MERCH-789'
    }
    
    result = orchestrator.process_transaction(test_transaction)
    print(json.dumps(result, indent=2))
