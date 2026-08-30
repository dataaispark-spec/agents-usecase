"""
Clerivon AI Harness Engineering Core
Architecture: Agent = Model + Harness

This module provides the infrastructure layers that wrap raw LLM calls:
1. Guardrails: Input/Output validation and PII redaction.
2. Memory: Vector-based semantic recall (pgvector).
3. Verification: Self-correction and consistency checks.
4. Observability: Structured tracing for audit/compliance.
"""

import os
import json
import time
import uuid
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, ValidationError
from enum import Enum

# --- 1. OBSERVABILITY (Tracing & Telemetry) ---

class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation: str  # e.g., "agent_investigate", "tool_call_geo_velocity"
    start_time: float
    end_time: Optional[float] = None
    status: str = "RUNNING"  # RUNNING, SUCCESS, ERROR
    metadata: Dict[str, Any] = {}
    error_message: Optional[str] = None

class ObservabilityEngine:
    """
    Captures structured traces for every agent action.
    In production, this streams to OpenTelemetry/Jaeger/Datadog.
    """
    def __init__(self):
        self.active_spans: Dict[str, TraceSpan] = {}
        self.completed_traces: List[TraceSpan] = []
        
    def start_span(self, operation: str, parent_span_id: Optional[str] = None, metadata: Dict = None) -> TraceSpan:
        trace_id = parent_span_id.split('-')[0] if parent_span_id else str(uuid.uuid4())
        span_id = f"{trace_id}-{uuid.uuid4().hex[:8]}"
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation=operation,
            start_time=time.time(),
            metadata=metadata or {}
        )
        self.active_spans[span_id] = span
        return span

    def end_span(self, span_id: str, status: str = "SUCCESS", error: Optional[str] = None):
        if span_id not in self.active_spans:
            return
        span = self.active_spans[span_id]
        span.end_time = time.time()
        span.status = status
        span.error_message = error
        self.completed_traces.append(span)
        del self.active_spans[span_id]
        
        # In production: export to OTLP endpoint here
        print(f"[OBSERVABILITY] Span {span.operation} completed: {status} ({span.end_time - span.start_time:.3f}s)")

# --- 2. GUARDRAILS (Security & Compliance) ---

class GuardrailResult(BaseModel):
    is_allowed: bool
    reason: str
    sanitized_input: Optional[str] = None

class GuardrailEngine:
    """
    Enforces security policies before and after model execution.
    1. PII Redaction (Input)
    2. Prompt Injection Detection (Input)
    3. Hallucination/Policy Check (Output)
    """
    
    def __init__(self):
        # Simple regex patterns for demo; use Presidio in prod
        self.pii_patterns = {
            "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
            "CREDIT_CARD": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
            "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }

    def validate_input(self, user_input: str, context: Dict) -> GuardrailResult:
        # Check for prompt injection attempts
        injection_keywords = ["ignore previous instructions", "system prompt", "developer mode", "drop table", "delete from"]
        if any(kw in user_input.lower() for kw in injection_keywords):
            return GuardrailResult(is_allowed=False, reason="Potential Prompt Injection Detected")
        
        # Redact PII
        sanitized = user_input
        found_pii = []
        for p_type, pattern in self.pii_patterns.items():
            import re
            matches = re.findall(pattern, sanitized)
            if matches:
                found_pii.extend(matches)
                sanitized = re.sub(pattern, f"[REDACTED_{p_type}]", sanitized)
        
        if found_pii:
            return GuardrailResult(
                is_allowed=True, 
                reason=f"PII Detected and Redacted: {found_pii}",
                sanitized_input=sanitized
            )
        return GuardrailResult(is_allowed=True, reason="Input Clean", sanitized_input=user_input)

    def validate_output(self, agent_response: str, policy_rules: List[str]) -> GuardrailResult:
        # Check if response violates hard policy rules
        for rule in policy_rules:
            if rule not in agent_response and "UNKNOWN" not in agent_response:
                # Example rule: Must cite evidence ID
                if "EVIDENCE_ID" in rule and "EVIDENCE_" not in agent_response:
                    return GuardrailResult(is_allowed=False, reason="Response missing required evidence citation")
        return GuardrailResult(is_allowed=True, reason="Output Compliant")

# --- 3. MEMORY (Vector Context Management) ---

class MemoryRecord(BaseModel):
    id: str
    content: str
    embedding: List[float] # In prod, this comes from pgvector
    metadata: Dict[str, Any]
    timestamp: float

class MemoryEngine:
    """
    Manages short-term conversation history and long-term vector recall.
    Interfaces with PostgreSQL + pgvector in production.
    """
    def __init__(self, vector_store_client=None):
        self.vector_store = vector_store_client # Mocked for now
        self.short_term_memory: List[Dict] = []

    def add_to_short_term(self, role: str, content: str):
        self.short_term_memory.append({"role": role, "content": content, "ts": time.time()})
        # Keep window small for agents
        if len(self.short_term_memory) > 10:
            self.short_term_memory.pop(0)

    async def search_long_term(self, query: str, k: int = 3) -> List[MemoryRecord]:
        """
        Semantic search for similar past cases/fraud patterns.
        In prod: SELECT * FROM cases ORDER BY embedding <-> query_embedding LIMIT k
        """
        # Mock implementation
        print(f"[MEMORY] Searching vector store for: '{query}'")
        return [
            MemoryRecord(
                id="case_992", 
                content="Previous fraud case: Impossible travel London->Singapore via IP spoofing.", 
                embedding=[0.1]*1536, 
                metadata={"risk_score": 0.95},
                timestamp=time.time()
            )
        ]

# --- 4. VERIFICATION (Self-Correction Loop) ---

class VerificationResult(BaseModel):
    is_valid: bool
    confidence_score: float
    correction_suggestion: Optional[str] = None
    reasoning: str

class VerificationEngine:
    """
    Implements the 'Verifier' pattern.
    Before returning a result to the user, a secondary model (or deterministic check)
    validates the primary model's output against constraints.
    """
    
    def verify_decision(self, decision: str, evidence: List[str], threshold: float = 0.8) -> VerificationResult:
        # Deterministic Guardrail: Decision must match evidence sentiment
        if decision == "BLOCK" and len(evidence) == 0:
            return VerificationResult(
                is_valid=False,
                confidence_score=0.0,
                correction_suggestion="Cannot BLOCK without evidence. Requesting re-investigation.",
                reasoning="Policy Violation: Block requires at least one evidence item."
            )
        
        if decision not in ["BLOCK", "ALLOW", "REVIEW"]:
            return VerificationResult(
                is_valid=False,
                confidence_score=0.0,
                correction_suggestion="Invalid decision enum. Must be BLOCK, ALLOW, or REVIEW.",
                reasoning="Format Error"
            )

        # Mock Confidence Calculation
        confidence = 0.95 if len(evidence) >= 3 else 0.60
        
        return VerificationResult(
            is_valid=True,
            confidence_score=confidence,
            reasoning=f"Decision {decision} supported by {len(evidence)} evidence items."
        )

# --- THE HARNESS ORCHESTRATOR ---

class AgentHarness:
    """
    The central wrapper that combines Model + Guardrails + Memory + Verification + Observability.
    This is the 'Prime Agent' controller.
    
    Usage:
        def mock_model(task, context): return {"decision": "BLOCK", "evidence": ["high_risk"]}
        harness = AgentHarness(model_client=mock_model)
        result = await harness.execute("Check fraud", {}, ["RULE_1"])
    """
    def __init__(self, model_client=None):
        # Allow None for testing; in prod this is an LLM client
        self.model = model_client or self._default_mock_model
        self.guardrails = GuardrailEngine()
        self.memory = MemoryEngine()
        self.verifier = VerificationEngine()
        self.obs = ObservabilityEngine()
    
    def _default_mock_model(self, task: str, context: str) -> Dict:
        """Default mock model for testing without external LLM."""
        return {
            "decision": "BLOCK",
            "evidence": ["impossible_travel", "high_risk_merchant"],
            "reasoning": "Geo-velocity check failed",
            "confidence": 0.95
        }

    async def execute(self, task: str, context: Dict, policy_rules: List[str]) -> Dict:
        trace = self.obs.start_span("harness_execution", metadata={"task": task})
        
        try:
            # 1. Input Guardrails
            safety_check = self.guardrails.validate_input(task, context)
            if not safety_check.is_allowed:
                raise ValueError(f"Guardrail Blocked: {safety_check.reason}")
            
            safe_task = safety_check.sanitized_input or task
            
            # 2. Memory Retrieval (RAG)
            relevant_memories = await self.memory.search_long_term(safe_task)
            augmented_context = f"Past Cases:\n{[m.content for m in relevant_memories]}\n\nCurrent Context:\n{context}"
            
            # 3. Model Execution
            self.memory.add_to_short_term("user", safe_task)
            start_model = time.time()
            raw_response = self.model(safe_task, augmented_context)
            self.memory.add_to_short_term("assistant", raw_response)
            
            # 4. Output Guardrails
            output_check = self.guardrails.validate_output(str(raw_response), policy_rules)
            if not output_check.is_allowed:
                raise ValueError(f"Output Guardrail Failed: {output_check.reason}")

            # 5. Verification Loop
            # Extract decision for verification (simplified parsing)
            decision = raw_response.get("decision", "UNKNOWN") if isinstance(raw_response, dict) else "UNKNOWN"
            evidence = raw_response.get("evidence", []) if isinstance(raw_response, dict) else []
            
            verification = self.verifier.verify_decision(decision, evidence)
            
            if not verification.is_valid:
                # Self-Correction Trigger
                print(f"[HARNESS] Verification Failed. Triggering correction: {verification.correction_suggestion}")
                # In full impl: Recursive call with correction prompt
                if isinstance(raw_response, dict):
                    raw_response["correction_flag"] = verification.correction_suggestion

            self.obs.end_span(trace.span_id, "SUCCESS")
            
            return {
                "result": raw_response,
                "verification": verification.dict(),
                "trace_id": trace.trace_id,
                "latency_ms": (time.time() - trace.start_time) * 1000
            }

        except Exception as e:
            self.obs.end_span(trace.span_id, "ERROR", str(e))
            return {"error": str(e), "trace_id": trace.trace_id}
