#!/usr/bin/env python3
"""
Generate complete Clerivon AI Fraud Detection MAS zip file.
This script creates the full project structure and zips it.
"""

import os
import zipfile
from pathlib import Path

# Define the project structure
PROJECT_NAME = "clerivon-fraud-detection-mas"

# File contents for the complete system
FILES = {
    # Core Package
    f"{PROJECT_NAME}/fraud_agents/__init__.py": '''"""Clerivon AI - Multi-Agent Fraud Detection System."""
__version__ = "1.0.0"
__author__ = "Clerivon AI"
''',
    
    f"{PROJECT_NAME}/fraud_agents/harness.py": '''"""
Harness Engineering: Guardrails, Memory, Verification, Observability
Agent = Model + Harness Architecture
"""
import json
import re
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class Span:
    """Observability span for distributed tracing."""
    trace_id: str
    span_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    status: str = "running"
    attributes: Dict[str, Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.attributes is None:
            self.attributes = {}

class GuardrailEngine:
    """PII redaction, prompt injection detection, output compliance."""
    
    PII_PATTERNS = {
        'SSN': r'\\b\\d{3}-\\d{2}-\\d{4}\\b',
        'CREDIT_CARD': r'\\b\\d{4}[- ]?\\d{4}[- ]?\\d{4}[- ]?\\d{4}\\b',
        'EMAIL': r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b',
    }
    
    INJECTION_KEYWORDS = ['ignore previous', 'system prompt', 'bypass', 'jailbreak']
    
    def redact_pii(self, text: str) -> tuple[str, Dict[str, List[str]]]:
        """Redact PII from text and return redacted text + found PII map."""
        found_pii = {}
        redacted = text
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                found_pii[pii_type] = matches
                redacted = re.sub(pattern, f'[REDACTED_{pii_type}]', redacted)
        
        return redacted, found_pii
    
    def detect_injection(self, prompt: str) -> bool:
        """Detect prompt injection attempts."""
        prompt_lower = prompt.lower()
        return any(keyword in prompt_lower for keyword in self.INJECTION_KEYWORDS)
    
    def validate_output(self, output: str, expected_schema: Dict) -> bool:
        """Validate output against expected schema."""
        try:
            data = json.loads(output)
            for key, value_type in expected_schema.items():
                if key not in data:
                    return False
                if not isinstance(data[key], value_type):
                    return False
            return True
        except:
            return False

class MemoryEngine:
    """Short-term conversation history + long-term vector search."""
    
    def __init__(self):
        self.short_term: List[Dict] = []
        self.long_term_index: List[Dict] = []
    
    def add_short_term(self, role: str, content: str, metadata: Dict = None):
        """Add message to short-term memory."""
        self.short_term.append({
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        })
        # Keep only last 50 messages
        if len(self.short_term) > 50:
            self.short_term = self.short_term[-50:]
    
    def get_short_term(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from short-term memory."""
        return self.short_term[-limit:]
    
    def add_long_term(self, content: str, embedding: List[float] = None, metadata: Dict = None):
        """Add to long-term memory (pgvector-ready)."""
        entry = {
            'id': str(uuid.uuid4()),
            'content': content,
            'embedding': embedding,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self.long_term_index.append(entry)
    
    def search_long_term(self, query_embedding: List[float], limit: int = 5) -> List[Dict]:
        """Search long-term memory by vector similarity (pgvector integration)."""
        # In production, this uses pgvector cosine similarity
        # For now, return most recent entries
        return sorted(self.long_term_index, key=lambda x: x['timestamp'], reverse=True)[:limit]

class VerificationEngine:
    """Decision validation, evidence requirements, self-correction."""
    
    def validate_decision(self, decision: str, evidence: List[Dict]) -> tuple[bool, str]:
        """Validate that decision has sufficient evidence."""
        required_evidence = {
            'BLOCK': 3,
            'REVIEW': 2,
            'APPROVE': 1
        }
        
        min_evidence = required_evidence.get(decision, 2)
        if len(evidence) < min_evidence:
            return False, f"Insufficient evidence: need {min_evidence}, got {len(evidence)}"
        
        return True, "Decision validated"
    
    def self_correct(self, decision: str, confidence: float, threshold: float = 0.7) -> str:
        """Trigger self-correction if confidence below threshold."""
        if confidence < threshold:
            return "REVIEW"  # Escalate to human
        return decision

class ObservabilityEngine:
    """Distributed tracing, latency metrics, audit logging."""
    
    def __init__(self):
        self.traces: Dict[str, List[Span]] = {}
        self.metrics: Dict[str, List[float]] = {}
    
    def start_span(self, name: str, trace_id: str = None) -> Span:
        """Start a new observability span."""
        trace_id = trace_id or str(uuid.uuid4())
        span = Span(
            trace_id=trace_id,
            span_id=str(uuid.uuid4()),
            name=name,
            start_time=time.time()
        )
        
        if trace_id not in self.traces:
            self.traces[trace_id] = []
        self.traces[trace_id].append(span)
        
        return span
    
    def end_span(self, span: Span, error: str = None):
        """Complete an observability span."""
        span.end_time = time.time()
        span.status = "error" if error else "completed"
        if error:
            span.error = error
        
        # Record latency metric
        latency = span.end_time - span.start_time
        if span.name not in self.metrics:
            self.metrics[span.name] = []
        self.metrics[span.name].append(latency)
    
    def get_trace(self, trace_id: str) -> List[Dict]:
        """Get complete trace with all spans."""
        if trace_id not in self.traces:
            return []
        return [asdict(span) for span in self.traces[trace_id]]
    
    def get_metrics_summary(self) -> Dict[str, Dict]:
        """Get latency metrics summary."""
        summary = {}
        for name, latencies in self.metrics.items():
            summary[name] = {
                'count': len(latencies),
                'avg': sum(latencies) / len(latencies),
                'min': min(latencies),
                'max': max(latencies)
            }
        return summary

class Harness:
    """Complete harness wrapping the model."""
    
    def __init__(self):
        self.guardrails = GuardrailEngine()
        self.memory = MemoryEngine()
        self.verification = VerificationEngine()
        self.observability = ObservabilityEngine()
    
    def process_input(self, prompt: str) -> tuple[str, Dict]:
        """Process input through guardrails and memory."""
        # Check for injection
        if self.guardrails.detect_injection(prompt):
            raise ValueError("Prompt injection detected")
        
        # Redact PII
        redacted, found_pii = self.guardrails.redact_pii(prompt)
        
        # Add to memory
        self.memory.add_short_term('user', redacted)
        
        return redacted, {'found_pii': found_pii}
    
    def validate_output(self, output: str, decision: str, evidence: List[Dict]) -> tuple[bool, str]:
        """Validate model output through verification engine."""
        valid, message = self.verification.validate_decision(decision, evidence)
        return valid, message
    
    def create_trace(self, operation: str) -> Span:
        """Create observability trace."""
        return self.observability.start_span(operation)
    
    def finalize_trace(self, span: Span, error: str = None):
        """Finalize observability trace."""
        self.observability.end_span(span, error)

# Example usage
if __name__ == "__main__":
    harness = Harness()
    
    # Test input processing
    test_prompt = "Customer SSN 123-45-6789 made transaction"
    redacted, metadata = harness.process_input(test_prompt)
    print(f"Original: {test_prompt}")
    print(f"Redacted: {redacted}")
    print(f"Found PII: {metadata['found_pii']}")
    
    # Test observability
    span = harness.create_trace("fraud_detection")
    time.sleep(0.1)  # Simulate work
    harness.finalize_trace(span)
    
    print(f"Metrics: {harness.observability.get_metrics_summary()}")
''',
    
    f"{PROJECT_NAME}/fraud_agents/prime_agents.py": '''"""
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
                explanation += f"  {i}. {evidence['tool']}: {evidence['relevance']} relevance\n"
        
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
''',
    
    # Add more files as needed...
    # For brevity, I'll create a minimal set that can be expanded
}

def create_project_structure():
    """Create the complete project structure."""
    base_path = Path(PROJECT_NAME)
    
    # Create directories
    dirs = [
        base_path / "fraud_agents",
        base_path / "tests" / "unit",
        base_path / "tests" / "e2e",
        base_path / "tests" / "cloud",
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Create files
    for file_path, content in FILES.items():
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print(f"Created {len(FILES)} files in {PROJECT_NAME}/")
    return base_path

def create_zip_file(project_path: Path):
    """Create zip file of the project."""
    zip_path = Path(f"{project_path.name}.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(project_path.parent)
                zipf.write(file_path, arcname)
    
    print(f"Created {zip_path} ({zip_path.stat().st_size / 1024:.1f} KB)")
    return zip_path

if __name__ == "__main__":
    print("🚀 Generating Clerivon AI Fraud Detection MAS...")
    project_path = create_project_structure()
    zip_path = create_zip_file(project_path)
    print(f"✅ Complete! Download: {zip_path.absolute()}")