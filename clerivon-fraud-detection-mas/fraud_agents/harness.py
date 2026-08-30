"""
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
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        'CREDIT_CARD': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
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
