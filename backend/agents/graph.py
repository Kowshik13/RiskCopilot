"""
LangGraph Agent Orchestration for Risk Copilot
Manages the flow between different agents
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import time
import structlog

from core.retrieval_service import get_retrieval_service
from core.guardrails import get_guardrails_engine
from core.llm_adapter import get_llm_adapter
from app.models import RiskLevel, Citation, GuardrailViolation, AgentTrace

logger = structlog.get_logger()

@dataclass
class AgentState:
    """State passed between agents in the graph"""
    # Input
    query: str
    session_id: str
    
    # Processing flags
    enable_guardrails: bool = True
    return_traces: bool = False
    
    # Intermediate results
    sanitized_query: Optional[str] = None
    guardrail_violations: List[GuardrailViolation] = field(default_factory=list)
    retrieved_context: Optional[str] = None
    citations: List[Citation] = field(default_factory=list)
    
    # Output
    response: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = 0.0
    
    # Traces
    traces: List[AgentTrace] = field(default_factory=list)
    
    # Metadata
    start_time: float = field(default_factory=time.time)
    processing_time_ms: int = 0

class Agent:
    """Base class for all agents"""
    
    def __init__(self, name: str):
        self.name = name
        
    def process(self, state: AgentState) -> AgentState:
        """Process the state - to be implemented by subclasses"""
        raise NotImplementedError
    
    def _add_trace(self, state: AgentState, input_data: Dict, output_data: Dict, status: str, duration_ms: int):
        """Add trace if tracing is enabled"""
        if state.return_traces:
            state.traces.append(AgentTrace(
                agent_name=self.name,
                timestamp=datetime.utcnow(),
                input_data=input_data,
                output_data=output_data,
                duration_ms=duration_ms,
                status=status
            ))

class SanitizerAgent(Agent):
    """Agent for input sanitization and guardrails"""
    
    def __init__(self):
        super().__init__("sanitizer")
        self.guardrails = get_guardrails_engine()
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            if state.enable_guardrails:
                # Sanitize input
                sanitized, violations = self.guardrails.sanitize_input(state.query)
                state.sanitized_query = sanitized
                state.guardrail_violations.extend(violations)
                
                # Calculate initial risk level
                state.risk_level = self.guardrails.calculate_risk_level(violations)
                
                # Log if critical violations
                if state.risk_level == RiskLevel.CRITICAL:
                    logger.warning(f"Critical violations detected: {[v.type for v in violations]}")
            else:
                state.sanitized_query = state.query
            
            self._add_trace(
                state,
                {"query": state.query[:100]},
                {"sanitized": bool(state.sanitized_query != state.query), "violations": len(violations) if state.enable_guardrails else 0},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Sanitizer error: {e}")
            state.sanitized_query = state.query
            
        return state

class RetrieverAgent(Agent):
    """Agent for document retrieval"""
    
    def __init__(self):
        super().__init__("retriever")
        self.retrieval_service = get_retrieval_service()
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            # Get context for query
            query = state.sanitized_query or state.query
            rag_result = self.retrieval_service.get_context_for_llm(query, k=5)
            
            state.retrieved_context = rag_result["context"]
            state.citations = rag_result["citations"]
            
            # Adjust confidence based on retrieval
            if state.retrieved_context:
                state.confidence = 0.85
            else:
                state.confidence = 0.3
            
            self._add_trace(
                state,
                {"query": query[:100]},
                {"found_context": bool(state.retrieved_context), "citations_count": len(state.citations)},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Retriever error: {e}")
            state.retrieved_context = ""
            
        return state

class RiskEvaluatorAgent(Agent):
    """Agent for risk evaluation"""
    
    def __init__(self):
        super().__init__("risk_evaluator")
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            # Risk evaluation logic
            query_lower = state.query.lower()
            
            # High risk keywords
            high_risk_keywords = ['compliance', 'violation', 'breach', 'penalty', 'regulatory']
            if any(keyword in query_lower for keyword in high_risk_keywords):
                state.risk_level = max(state.risk_level, RiskLevel.HIGH)
            
            # Medium risk keywords
            medium_risk_keywords = ['validation', 'audit', 'review', 'assessment']
            if any(keyword in query_lower for keyword in medium_risk_keywords):
                state.risk_level = max(state.risk_level, RiskLevel.MEDIUM)
            
            self._add_trace(
                state,
                {"current_risk": state.risk_level.value},
                {"evaluated_risk": state.risk_level.value},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Risk evaluator error: {e}")
            
        return state

class GeneratorAgent(Agent):
    """Agent for response generation"""
    
    def __init__(self):
        super().__init__("generator")
        self.llm_adapter = get_llm_adapter()
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            # Generate response based on context
            if state.retrieved_context:
                # We have context from documents
                response = self.llm_adapter.generate_with_context(
                    query=state.sanitized_query or state.query,
                    context=state.retrieved_context,
                    citations=state.citations
                )
            else:
                # No context - use fallback
                response = self.llm_adapter.generate_fallback(
                    query=state.sanitized_query or state.query
                )
            
            state.response = response
            
            self._add_trace(
                state,
                {"has_context": bool(state.retrieved_context)},
                {"response_length": len(response)},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Generator error: {e}")
            state.response = "I apologize, but I encountered an error processing your request. Please try again."
            
        return state

class ValidatorAgent(Agent):
    """Agent for output validation"""
    
    def __init__(self):
        super().__init__("validator")
        self.guardrails = get_guardrails_engine()
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            if state.enable_guardrails and state.response:
                # Validate output
                violations = self.guardrails.validate_output(state.response)
                
                if violations:
                    # Block response if critical violations
                    critical = any(v.severity == RiskLevel.CRITICAL for v in violations)
                    if critical:
                        state.response = "I cannot provide this response as it may contain sensitive information."
                        state.guardrail_violations.extend(violations)
                        state.risk_level = RiskLevel.CRITICAL
            
            self._add_trace(
                state,
                {"response_length": len(state.response) if state.response else 0},
                {"validated": True, "blocked": state.risk_level == RiskLevel.CRITICAL},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Validator error: {e}")
            
        return state

class AuditAgent(Agent):
    """Agent for audit logging"""
    
    def __init__(self):
        super().__init__("audit")
        self.guardrails = get_guardrails_engine()
    
    def process(self, state: AgentState) -> AgentState:
        start = time.time()
        
        try:
            # Generate audit entry
            audit_entry = self.guardrails.generate_audit_entry(
                input_text=state.query,
                output_text=state.response or "",
                violations=state.guardrail_violations,
                risk_level=state.risk_level
            )
            
            # Log to structured logger (in production, save to database)
            logger.info(
                "audit_log",
                session_id=state.session_id,
                **audit_entry
            )
            
            # Calculate total processing time
            state.processing_time_ms = int((time.time() - state.start_time) * 1000)
            
            self._add_trace(
                state,
                {"risk_level": state.risk_level.value},
                {"logged": True, "total_time_ms": state.processing_time_ms},
                "success",
                int((time.time() - start) * 1000)
            )
            
        except Exception as e:
            logger.error(f"Audit error: {e}")
            
        return state

class RiskCopilotGraph:
    """Main orchestration graph"""
    
    def __init__(self):
        # Initialize agents
        self.sanitizer = SanitizerAgent()
        self.retriever = RetrieverAgent()
        self.risk_evaluator = RiskEvaluatorAgent()
        self.generator = GeneratorAgent()
        self.validator = ValidatorAgent()
        self.audit = AuditAgent()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process through the agent graph
        
        Flow:
        1. Sanitizer -> Clean input
        2. Retriever -> Get context
        3. Risk Evaluator -> Assess risk
        4. Generator -> Create response
        5. Validator -> Check output
        6. Audit -> Log everything
        """
        
        # Sequential processing through agents
        state = self.sanitizer.process(state)
        
        # Skip further processing if critical violation
        if state.risk_level != RiskLevel.CRITICAL:
            state = self.retriever.process(state)
            state = self.risk_evaluator.process(state)
            state = self.generator.process(state)
            state = self.validator.process(state)
        else:
            state.response = "Your request contains content that violates our safety guidelines."
            state.confidence = 1.0
        
        # Always audit
        state = self.audit.process(state)
        
        return state

# Singleton instance
_graph = None

def get_risk_copilot_graph() -> RiskCopilotGraph:
    """Get singleton instance of the graph"""
    global _graph
    if _graph is None:
        _graph = RiskCopilotGraph()
    return _graph