"""
Retrieval Service for Risk Copilot
Handles document retrieval and citation generation
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import structlog

from core.faiss_index import FAISSIndex
from app.config import settings
from app.models import Citation

logger = structlog.get_logger()

class RetrievalService:
    """
    Service for retrieving relevant documents and generating citations
    """
    
    def __init__(self, index_path: str = None):
        """
        Initialize retrieval service
        
        Args:
            index_path: Path to FAISS index (uses default from settings if None)
        """
        self.index_path = index_path or settings.FAISS_INDEX_PATH
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or load the FAISS index"""
        try:
            self.index = FAISSIndex(
                index_path=self.index_path,
                embedding_model=settings.EMBEDDING_MODEL
            )
            
            # Try to load existing index
            if self.index.exists():
                success = self.index.load()
                if success:
                    stats = self.index.get_stats()
                    logger.info(f"Loaded index with {stats['total_vectors']} vectors")
                else:
                    logger.warning("Failed to load index, will work without RAG")
                    self.index = None
            else:
                logger.warning("Index does not exist, will work without RAG")
                self.index = None
                
        except Exception as e:
            logger.error(f"Error initializing index: {e}")
            self.index = None
    
    def retrieve(
        self,
        query: str,
        k: int = 5,
        score_threshold: float = 0.5,
        filter_doc: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            filter_doc: Optional document name to filter by
            
        Returns:
            List of retrieved documents with metadata
        """
        if self.index is None:
            logger.warning("Index not initialized, returning empty results")
            return []
        
        try:
            # Perform search
            if filter_doc:
                results = self.index.search_with_filter(
                    query=query,
                    filter_dict={"document_name": filter_doc},
                    k=k
                )
            else:
                results = self.index.search(
                    query=query,
                    k=k,
                    score_threshold=score_threshold
                )
            
            logger.info(f"Retrieved {len(results)} documents for query: '{query[:50]}...'")
            return results
            
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
    
    def generate_citations(
        self,
        retrieved_docs: List[Dict[str, Any]],
        min_score: float = 0.6
    ) -> List[Citation]:
        """
        Generate citations from retrieved documents
        
        Args:
            retrieved_docs: List of retrieved documents
            min_score: Minimum score for citation
            
        Returns:
            List of Citation objects
        """
        citations = []
        
        # Track unique sources to avoid duplicates
        seen_chunks = set()
        
        for doc in retrieved_docs:
            if doc['score'] < min_score:
                continue
            
            chunk_id = doc['metadata'].get('chunk_id')
            if chunk_id in seen_chunks:
                continue
            
            seen_chunks.add(chunk_id)
            
            # Create citation
            citation = Citation(
                source_id=doc['metadata'].get('document_id', 'unknown'),
                document_name=doc['metadata'].get('document_name', 'Unknown Document'),
                page_number=doc['metadata'].get('chunk_index'),  # Using chunk index as page proxy
                section=doc['metadata'].get('section'),
                relevance_score=doc['score'],
                excerpt=doc['content'][:200] + "..." if len(doc['content']) > 200 else doc['content']
            )
            citations.append(citation)
        
        logger.info(f"Generated {len(citations)} citations")
        return citations
    
    def get_context_for_llm(
        self,
        query: str,
        k: int = 5,
        max_context_length: int = 3000
    ) -> Dict[str, Any]:
        """
        Get context for LLM including retrieved documents
        
        Args:
            query: User query
            k: Number of documents to retrieve
            max_context_length: Maximum length of context
            
        Returns:
            Dict with context and citations
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, k=k)
        
        if not retrieved_docs:
            return {
                "context": "",
                "citations": [],
                "sources": []
            }
        
        # Build context string
        context_parts = []
        total_length = 0
        used_docs = []
        
        for doc in retrieved_docs:
            doc_text = f"[Source: {doc['metadata']['document_name']}]\n{doc['content']}\n"
            doc_length = len(doc_text)
            
            if total_length + doc_length > max_context_length:
                break
            
            context_parts.append(doc_text)
            total_length += doc_length
            used_docs.append(doc)
        
        context = "\n---\n".join(context_parts)
        
        # Generate citations
        citations = self.generate_citations(used_docs)
        
        return {
            "context": context,
            "citations": citations,
            "sources": [doc['metadata']['document_name'] for doc in used_docs],
            "num_sources": len(used_docs)
        }
    
    def search_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Search for documents related to a specific topic
        
        Args:
            topic: Topic to search for
            
        Returns:
            List of relevant documents
        """
        # Define topic-specific queries
        topic_queries = {
            "model_risk": [
                "model risk management",
                "model validation requirements",
                "model governance framework"
            ],
            "ai_ethics": [
                "AI ethics principles",
                "ethical AI development",
                "bias and fairness in AI"
            ],
            "llm": [
                "large language models",
                "LLM governance",
                "prompt engineering",
                "hallucination risks"
            ],
            "compliance": [
                "regulatory compliance",
                "EU AI Act",
                "Basel requirements",
                "audit requirements"
            ]
        }
        
        # Get queries for topic
        queries = topic_queries.get(topic.lower(), [topic])
        
        # Aggregate results
        all_results = []
        seen_chunks = set()
        
        for query in queries:
            results = self.retrieve(query, k=3)
            for result in results:
                chunk_id = result['metadata'].get('chunk_id')
                if chunk_id not in seen_chunks:
                    seen_chunks.add(chunk_id)
                    all_results.append(result)
        
        # Sort by score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        
        return all_results[:5]  # Return top 5
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the index"""
        if self.index is None:
            return {"status": "not_initialized"}
        
        return self.index.get_stats()
    
    def refresh_index(self) -> bool:
        """Refresh the index from disk"""
        try:
            self._initialize_index()
            return self.index is not None
        except Exception as e:
            logger.error(f"Error refreshing index: {e}")
            return False


# Singleton instance
_retrieval_service = None

def get_retrieval_service() -> RetrievalService:
    """
    Get singleton instance of retrieval service
    
    Returns:
        RetrievalService instance
    """
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
    return _retrieval_service