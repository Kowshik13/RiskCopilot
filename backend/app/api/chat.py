"""
Chat endpoint for Risk Copilot API
Final implementation with LangGraph orchestration
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import structlog

from app.models import ChatRequest, ChatResponse
from agents.graph import get_risk_copilot_graph, AgentState

router = APIRouter()
logger = structlog.get_logger()

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user queries through the multi-agent system
    """
    # Generate IDs
    message_id = str(uuid.uuid4())
    session_id = request.session_id or str(uuid.uuid4())
    
    logger.info(f"Processing chat request", 
                message_id=message_id, 
                session_id=session_id)
    
    try:
        # Create initial state
        state = AgentState(
            query=request.message,
            session_id=session_id,
            enable_guardrails=request.enable_guardrails,
            return_traces=request.return_traces
        )
        
        # Get the graph and process
        graph = get_risk_copilot_graph()
        state = graph.process(state)
        
        # Build response
        response = ChatResponse(
            message_id=message_id,
            session_id=session_id,
            question=request.message,
            answer=state.response or "Unable to generate response",
            risk_level=state.risk_level,
            confidence=state.confidence,
            citations=state.citations,
            guardrail_violations=state.guardrail_violations,
            traces=state.traces if request.return_traces else None,
            processing_time_ms=state.processing_time_ms,
            timestamp=datetime.utcnow()
        )
        
        logger.info(f"Request processed successfully",
                   message_id=message_id,
                   risk_level=state.risk_level.value,
                   processing_time_ms=state.processing_time_ms)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing chat request", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/sessions/{session_id}/history")
async def get_chat_history(session_id: str, limit: int = 20):
    """Retrieve chat history for a session"""
    return {
        "session_id": session_id,
        "messages": [],
        "total_count": 0
    }

@router.get("/chat/index/stats")
async def get_index_stats():
    """Get FAISS index statistics"""
    from core.retrieval_service import get_retrieval_service
    retrieval_service = get_retrieval_service()
    return retrieval_service.get_index_stats()