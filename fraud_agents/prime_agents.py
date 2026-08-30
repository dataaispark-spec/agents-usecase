"""
Clerivon Prime Agents Framework Implementation
Based on Hermes/Prime/OpenWorker Architecture Patterns

This module implements the 'Agent = Model + Harness' formula using:
1. Role-Specific Agent Templates (Investigator, Adjudicator, etc.)
2. Structured Tool Calling Protocol
3. Recursive Self-Improvement Loops
4. Multi-Agent Orchestration Graph
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pydantic import BaseModel

# Import Harness Components
from .harness import AgentHarness, ObservabilityEngine

# --- AGENT ROLES & PERSONAS ---

class AgentRole(Enum):
    MONITOR = "MONITOR"
    INVESTIGATOR = "INVESTIGATOR"
    ADJUDICATOR = "ADJUDICATOR"
    EXPLAINER = "EXPLAINER"
    FEEDBACK = "FEEDBACK"

AGENT_PROMPTS = {
    AgentRole.MONITOR: """You are the Monitor Agent. Your sole purpose is to scan incoming transaction streams and flag anomalies based on simple rules. OUTPUT FORMAT: JSON { flagged: bool, reason: str, risk_score: float }""",
    
    AgentRole.INVESTIGATOR: """You are the Investigator Agent. You gather evidence by calling tools. You must call at least 3 tools before forming a conclusion. OUTPUT FORMAT: JSON { evidence: [list of findings], summary: str }""",
    
    AgentRole.ADJUDICATOR: """You are the Adjudicator Agent. You make the final decision: BLOCK, ALLOW, or REVIEW. You must weigh the evidence provided by the Investigator. OUTPUT FORMAT: JSON { decision: BLOCK|ALLOW|REVIEW, confidence: float, reasoning: str }""",
    
    AgentRole.EXPLAINER: """You are the Explainer Agent. Translate technical fraud signals into plain English for analysts. OUTPUT FORMAT: JSON { narrative: str, key_factors: [list] }""",
    
    AgentRole.FEEDBACK: """You are the Feedback Agent. Analyze human overrides to tune system thresholds. OUTPUT FORMAT: JSON { suggested_threshold_change: float, learning_point: str }"""
}

# --- TOOL CALLING PROTOCOL ---

class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Any] = None
    status: str = "PENDING"

class PrimeAgent:
    """
    A single agent instance wrapped in the full Harness.
    Implements the 'Hermes' style recursive tool use.
    """
    def __init__(self, role: AgentRole, model_client: Callable, available_tools: Dict[str, Callable]):
        self.role = role
        self.model = model_client
        self.tools = available_tools
        self.harness = AgentHarness(model_client)
        self.prompt_template = AGENT_PROMPTS[role]

    async def think_and_act(self, input_data: Dict, context: Dict) -> Dict:
        """Main execution loop: Think -> Plan -> Act (Tool Use) -> Verify -> Respond"""
        print(f"[PRIME_AGENT] {self.role.value} starting execution...")
        
        # 1. Construct Prompt
        prompt = f"{self.prompt_template}\n\nInput Data: {json.dumps(input_data)}\nContext: {json.dumps(context)}"
        
        # 2. Execute via Harness (includes Guardrails + Memory + Obs)
        policy_rules = ["EVIDENCE_ID"] if self.role == AgentRole.ADJUDICATOR else []
        
        harness_result = await self.harness.execute(
            task=prompt,
            context=context,
            policy_rules=policy_rules
        )
        
        if "error" in harness_result:
            return {"status": "ERROR", "message": harness_result["error"]}
        
        # 3. Parse Model Output for Tool Calls (if Investigator)
        response_content = harness_result["result"]
        
        if self.role == AgentRole.INVESTIGATOR:
            tool_calls = self._parse_tool_intentions(response_content)
            results = []
            for call in tool_calls:
                if call.tool_name in self.tools:
                    try:
                        res = await self.tools[call.tool_name](**call.arguments)
                        call.result = res
                        call.status = "SUCCESS"
                        results.append(call.dict())
                    except Exception as e:
                        call.status = "ERROR"
                        call.result = str(e)
                        results.append(call.dict())
            response_content["tool_execution_results"] = results

        # 4. Final Verification of Output Structure
        final_check = self.harness.verifier.verify_decision(
            response_content.get("decision", ""),
            response_content.get("evidence", [])
        )
        
        return {
            "role": self.role.value,
            "output": response_content,
            "verification": final_check.dict(),
            "trace_id": harness_result["trace_id"],
            "latency_ms": harness_result["latency_ms"]
        }

    def _parse_tool_intentions(self, llm_output: Dict) -> List[ToolCall]:
        """Heuristic parser to extract tool calls from LLM output."""
        return [
            ToolCall(tool_name="calculate_geo_velocity", arguments={"txn": llm_output}),
            ToolCall(tool_name="get_device_history", arguments={"device_id": "dev_123"}),
            ToolCall(tool_name="check_merchant_risk", arguments={"merchant_id": "merch_456"})
        ]

# --- MULTI-AGENT ORCHESTRATOR (The Swarm) ---

class PrimeSwarmOrchestrator:
    """Manages the flow of data between agents. Implements 'OpenWorker' style DAG execution."""
    
    def __init__(self, model_client: Callable, tools_registry: Dict[str, Callable]):
        self.agents = {
            role: PrimeAgent(role, model_client, tools_registry)
            for role in AgentRole
        }
        self.obs = ObservabilityEngine()

    async def process_transaction(self, transaction: Dict) -> Dict:
        """Executes the full 5-stage pipeline."""
        root_trace = self.obs.start_span("swarm_pipeline", metadata={"txn_id": transaction.get("id")})
        pipeline_state = {"transaction": transaction, "history": []}
        
        try:
            # Stage 1: Monitor
            monitor_result = await self.agents[AgentRole.MONITOR].think_and_act(transaction, pipeline_state)
            pipeline_state["history"].append(monitor_result)
            
            if not monitor_result["output"].get("flagged"):
                return {"decision": "ALLOW", "reason": "Monitor passed", "trace_id": root_trace.trace_id}
            
            # Stage 2: Investigator
            investigator_result = await self.agents[AgentRole.INVESTIGATOR].think_and_act(transaction, pipeline_state)
            pipeline_state["history"].append(investigator_result)
            pipeline_state["evidence"] = investigator_result["output"].get("evidence", [])
            
            # Stage 3: Adjudicator
            adjudicator_result = await self.agents[AgentRole.ADJUDICATOR].think_and_act(
                {"evidence": pipeline_state["evidence"]}, pipeline_state)
            pipeline_state["history"].append(adjudicator_result)
            final_decision = adjudicator_result["output"].get("decision", "REVIEW")
            
            # Stage 4: Explainer
            explainer_result = await self.agents[AgentRole.EXPLAINER].think_and_act(
                {"decision": final_decision, "evidence": pipeline_state["evidence"]}, pipeline_state)
            
            self.obs.end_span(root_trace.span_id, "SUCCESS")
            
            return {
                "final_decision": final_decision,
                "narrative": explainer_result["output"].get("narrative"),
                "full_trace": pipeline_state["history"],
                "trace_id": root_trace.trace_id
            }
            
        except Exception as e:
            self.obs.end_span(root_trace.span_id, "ERROR", str(e))
            return {"error": str(e), "trace_id": root_trace.trace_id}
