"""
Chat endpoint for Risk Copilot API
Phase 2: Integrated with FAISS retrieval
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from datetime import datetime
import uuid
import time
import structlog
from typing import Optional

from app.models import (
    ChatRequest, 
    ChatResponse, 
    RiskLevel,
    Citation,
    GuardrailViolation,
    AgentTrace
)
from app.config import settings
from core.retrieval_service import get_retrieval_service

router = APIRouter()
logger = structlog.get_logger()

async def process_with_agents(
    message: str, 
    session_id: str, 
    enable_guardrails: bool,
    retrieval_service
):
    """
    Process message through agent pipeline with RAG
    """
    # Get context from RAG
    rag_result = retrieval_service.get_context_for_llm(message, k=5)
    
    # Determine risk level based on query
    risk_level = RiskLevel.LOW
    violations = []
    
    if enable_guardrails:
        # Check for PII patterns
        pii_patterns = ["password", "ssn", "credit card", "social security"]
        if any(pattern in message.lower() for pattern in pii_patterns):
            violations.append(
                GuardrailViolation(
                    type="pii",
                    severity=RiskLevel.HIGH,
                    description="Potential PII detected in input",
                    detected_content="[REDACTED]"
                )
            )
            risk_level = RiskLevel.HIGH
    
    # Generate response based on context
    if rag_result["context"]:
        # We have relevant context from documents
        answer = f"""Based on the policy documents, here's what I found regarding your query:

{rag_result['context'][:500]}...

This information comes from {rag_result['num_sources']} source(s) in our policy database.
"""
        confidence = 0.85
    else:
        # No relevant context found
        if settings.USE_MOCK_LLM:
            answer = f"I couldn't find specific information about '{message}' in the policy documents. This would typically trigger an LLM response, but we're in mock mode."
        else:
            answer = "I couldn't find specific information in the policy documents. Please try rephrasing your question or ask about model risk management, AI governance, or compliance topics."
        confidence = 0.3
        risk_level = RiskLevel.MEDIUM
    
    return {
        "answer": answer,
        "risk_level": risk_level,
        "citations": rag_result.get("citations", []),
        "violations": violations,
        "confidence": confidence,
        "context_used": bool(rag_result["context"])
    }

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user queries through the multi-agent system
    Now with actual RAG retrieval!
    """
    start_time = time.time()
    
    # Generate IDs
    message_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Processing chat request with RAG", 
                message_id=message_id, 
                session_id=session_id,
                message_length=len(request.message))
    
    try:
        # Get retrieval service
        retrieval_service = get_retrieval_service()
        
        # Check if index is available
        stats = retrieval_service.get_index_stats()
        if stats.get("status") == "not_initialized":
            logger.warning("FAISS index not initialized - working without RAG")
        
        # Process through agents with RAG
        result = await process_with_agents(
            message=request.message,
            session_id=session_id,
            enable_guardrails=request.enable_guardrails,
            retrieval_service=retrieval_service
        )
        
        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)
        
        # Add traces if requested
        traces = None
        if request.return_traces:
            traces = [
                AgentTrace(
                    agent_name="retriever",
                    timestamp=datetime.utcnow(),
                    input_data={"query": request.message},
                    output_data={
                        "found_context": result["context_used"],
                        "num_citations": len(result["citations"])
                    },
                    duration_ms=processing_time // 3,
                    status="success"
                ),
                AgentTrace(
                    agent_name="generator",
                    timestamp=datetime.utcnow(),
                    input_data={"has_context": result["context_used"]},
                    output_data={"response_length": len(result["answer"])},
                    duration_ms=processing_time // 2,
                    status="success"
                )
            ]
        
        # Build response
        response = ChatResponse(
            message_id=message_id,
            session_id=session_id,
            question=request.message,
            answer=result["answer"],
            risk_level=result["risk_level"],
            confidence=result["confidence"],
            citations=result["citations"],
            guardrail_violations=result["violations"],
            traces=traces,
            processing_time_ms=processing_time,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Chat request processed with RAG",
                   message_id=message_id,
                   processing_time_ms=processing_time,
                   risk_level=result["risk_level"],
                   citations_count=len(result["citations"]),
                   context_used=result["context_used"])
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request",
                    message_id=message_id,
                    error=str(e))
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

@router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str, limit: int = 20):
    """
    Retrieve chat history for a session
    """
    # Placeholder - will be implemented with actual storage
    return {
        "session_id": session_id,
        "messages": [],
        "total_count": 0
    }

@router.get("/chat/index/stats")
async def get_index_stats():
    """
    Get FAISS index statistics
    """
    retrieval_service = get_retrieval_service()
    return retrieval_service.get_index_stats()