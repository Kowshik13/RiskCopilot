"""
LLM Adapter for Risk Copilot
Supports OpenAI, mock mode, and fallback responses
"""

import os
from typing import List, Optional
from app.config import settings
from app.models import Citation
import structlog

logger = structlog.get_logger()

class LLMAdapter:
    """Adapter for LLM interactions with fallback support"""
    
    def __init__(self):
        self.use_mock = settings.USE_MOCK_LLM
        self.openai_client = None
        
        if not self.use_mock and settings.OPENAI_API_KEY:
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("OpenAI client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}, falling back to mock")
                self.use_mock = True
    
    def generate_with_context(
        self, 
        query: str, 
        context: str, 
        citations: List[Citation]
    ) -> str:
        """
        Generate response with RAG context
        """
        if self.use_mock:
            return self._mock_response_with_context(query, context, citations)
        
        if self.openai_client:
            try:
                # Build prompt
                prompt = f"""You are a Risk Management AI Assistant for a major bank. 
                Answer the following question based on the provided context from policy documents.
                Be precise, professional, and cite sources when possible.
                
                Context from policy documents:
                {context[:2000]}  # Limit context size
                
                Question: {query}
                
                Answer:"""
                
                response = self.openai_client.chat.completions.create(
                    model=settings.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a risk management expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=settings.TEMPERATURE,
                    max_tokens=settings.MAX_TOKENS
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                return self._mock_response_with_context(query, context, citations)
        
        return self._mock_response_with_context(query, context, citations)
    
    def generate_fallback(self, query: str) -> str:
        """
        Generate response without context
        """
        if self.use_mock:
            return self._mock_fallback_response(query)
        
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=settings.DEFAULT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a risk management expert. Provide general guidance."},
                        {"role": "user", "content": query}
                    ],
                    temperature=settings.TEMPERATURE,
                    max_tokens=500
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"OpenAI error: {e}")
                return self._mock_fallback_response(query)
        
        return self._mock_fallback_response(query)
    
    def _mock_response_with_context(self, query: str, context: str, citations: List[Citation]) -> str:
        """
        Mock response when context is available
        """
        # Extract key points from context
        context_preview = context[:500] if context else "No context available"
        
        response = f"""Based on the relevant policy documents, here's the information regarding your query:

**Key Finding:**
{context_preview}

**Summary:**
The policy documents indicate specific requirements and procedures that must be followed. """

        if citations:
            response += f"\n\n**Sources:**\n"
            for i, citation in enumerate(citations[:3], 1):
                response += f"{i}. {citation.document_name} - {citation.section or 'General'}\n"
        
        response += f"\n\nThis response is based on {len(citations)} relevant policy sections with an average relevance score of {sum(c.relevance_score for c in citations)/len(citations):.2f} if citations else 0."
        
        return response
    
    def _mock_fallback_response(self, query: str) -> str:
        """
        Mock response when no context is available
        """
        query_lower = query.lower()
        
        # Provide topic-specific responses
        if "model risk" in query_lower:
            return """Model risk refers to the potential for adverse consequences from decisions based on incorrect or misused model outputs. 

Key aspects include:
- Fundamental errors in methodology
- Implementation mistakes
- Using models outside intended purpose
- Data quality issues
- Performance degradation

For specific requirements, please refer to the Model Risk Management Policy."""
        
        elif "ai" in query_lower or "llm" in query_lower:
            return """AI governance ensures responsible and ethical AI deployment in banking contexts.

Key principles:
- Transparency and explainability
- Fairness and non-discrimination
- Security and privacy
- Human oversight
- Regulatory compliance

Consult the AI Governance Policy for detailed requirements."""
        
        elif "compliance" in query_lower or "regulatory" in query_lower:
            return """Regulatory compliance in banking involves adhering to laws and regulations.

Important areas:
- Basel III/IV requirements
- EU AI Act compliance
- GDPR for data protection
- Anti-money laundering (AML)
- Know Your Customer (KYC)

Specific requirements vary by jurisdiction and business area."""
        
        else:
            return f"""I understand you're asking about: "{query}"

While I don't have specific policy documents that directly address this query, I can provide general risk management guidance. For authoritative information, please consult:

1. Model Risk Management Policy - for model-related queries
2. AI Governance Policy - for AI/ML topics
3. Operational Risk Framework - for operational concerns

Would you like to rephrase your question or ask about a specific policy area?"""

# Singleton instance
_llm_adapter = None

def get_llm_adapter() -> LLMAdapter:
    """Get singleton instance of LLM adapter"""
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = LLMAdapter()
    return _llm_adapter