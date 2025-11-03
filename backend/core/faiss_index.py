"""
FAISS Vector Store for RAG implementation
Phase 2: Full implementation with actual FAISS operations
"""

import os
import pickle
import json
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
import structlog

logger = structlog.get_logger()

class FAISSIndex:
    """
    FAISS index wrapper for document retrieval with semantic search
    """
    
    def __init__(
        self, 
        index_path: str, 
        embedding_dim: int = 384,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
        """
        Initialize FAISS index
        
        Args:
            index_path: Path to store/load index
            embedding_dim: Dimension of embeddings
            embedding_model: Model for generating query embeddings
        """
        self.index_path = Path(index_path)
        self.embedding_dim = embedding_dim
        self.index = None
        self.chunks = []
        self.documents = {}
        
        # Initialize embedding model for queries
        logger.info(f"Initializing FAISS index with {embedding_model}")
        self.embedder = SentenceTransformer(embedding_model)
        
        # Create directory if it doesn't exist
        self.index_path.mkdir(parents=True, exist_ok=True)
        
    def exists(self) -> bool:
        """Check if index exists on disk"""
        return (self.index_path / "faiss.index").exists()
    
    def create_index(self, embeddings: np.ndarray, chunks: List[Dict], documents: Dict[str, Any]):
        """
        Create FAISS index from embeddings
        
        Args:
            embeddings: Numpy array of embeddings
            chunks: List of chunk dictionaries
            documents: Document metadata dict
        """
        if len(embeddings) == 0:
            raise ValueError("No embeddings provided")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index (using Inner Product for cosine similarity after L2 norm)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        
        # Add vectors to index
        self.index.add(embeddings)
        
        # Store metadata
        self.chunks = chunks
        self.documents = documents
        
        logger.info(f"Created FAISS index with {len(embeddings)} vectors")
    
    def load(self):
        """Load index from disk"""
        try:
            # Load FAISS index
            index_file = self.index_path / "faiss.index"
            if index_file.exists():
                self.index = faiss.read_index(str(index_file))
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
            
            # Load chunks
            chunks_file = self.index_path / "chunks.json"
            if chunks_file.exists():
                with open(chunks_file, "r", encoding="utf-8") as f:
                    self.chunks = json.load(f)
            
            # Load document metadata
            docs_file = self.index_path / "documents.json"
            if docs_file.exists():
                with open(docs_file, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            
            logger.info(f"Loaded {len(self.chunks)} chunks from {len(self.documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            return False
    
    def save(self):
        """Save index to disk"""
        try:
            # Save FAISS index
            if self.index is not None:
                index_file = self.index_path / "faiss.index"
                faiss.write_index(self.index, str(index_file))
            
            # Save chunks
            chunks_file = self.index_path / "chunks.json"
            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump(self.chunks, f, indent=2, ensure_ascii=False)
            
            # Save document metadata
            docs_file = self.index_path / "documents.json"
            with open(docs_file, "w", encoding="utf-8") as f:
                json.dump(self.documents, f, indent=2)
            
            logger.info("FAISS index saved successfully")
            
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        k: int = 5,
        score_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search
        
        Args:
            query: Search query
            k: Number of results to return
            score_threshold: Minimum similarity score
            
        Returns:
            List of search results with content and metadata
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Index is empty or not initialized")
            return []
        
        # Generate query embedding
        query_embedding = self.embedder.encode([query], convert_to_numpy=True)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search in index
        scores, indices = self.index.search(query_embedding, min(k, self.index.ntotal))
        
        # Prepare results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:  # FAISS returns -1 for empty results
                continue
                
            if score < score_threshold:
                continue
            
            chunk = self.chunks[idx]
            
            # Get document metadata
            doc_id = chunk["metadata"]["id"]
            doc_metadata = self.documents.get(doc_id, {})
            
            result = {
                "content": chunk["content"],
                "score": float(score),
                "metadata": {
                    "chunk_id": chunk["metadata"].get("chunk_id"),
                    "document_id": doc_id,
                    "document_name": doc_metadata.get("name", "Unknown"),
                    "section": chunk["metadata"].get("section"),
                    "chunk_index": chunk["metadata"].get("chunk_index"),
                    "total_chunks": chunk["metadata"].get("total_chunks")
                }
            }
            results.append(result)
        
        logger.info(f"Found {len(results)} results for query: '{query[:50]}...'")
        return results
    
    def search_with_filter(
        self, 
        query: str,
        filter_dict: Dict[str, Any],
        k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search with metadata filtering
        
        Args:
            query: Search query
            filter_dict: Metadata filters
            k: Number of results
            
        Returns:
            Filtered search results
        """
        # Get more results initially
        results = self.search(query, k=k*3)
        
        # Filter results
        filtered = []
        for result in results:
            match = True
            for key, value in filter_dict.items():
                if result["metadata"].get(key) != value:
                    match = False
                    break
            
            if match:
                filtered.append(result)
            
            if len(filtered) >= k:
                break
        
        return filtered[:k]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if self.index is None:
            return {"status": "not_initialized"}
        
        return {
            "total_vectors": self.index.ntotal,
            "total_chunks": len(self.chunks),
            "total_documents": len(self.documents),
            "embedding_dim": self.embedding_dim,
            "index_size_bytes": self.index.ntotal * self.embedding_dim * 4  # Approximate
        }
    
    def clear(self):
        """Clear the index"""
        self.index = None
        self.chunks = []
        self.documents = {}
        logger.info("Index cleared")
    
    def rebuild_from_processed(self, processed_dir: str):
        """
        Rebuild index from processed data
        
        Args:
            processed_dir: Directory containing processed data
        """
        processed_path = Path(processed_dir)
        
        # Load embeddings
        embeddings = np.load(processed_path / "embeddings.npy")
        
        # Load chunks
        with open(processed_path / "chunks.json", "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        # Load documents
        with open(processed_path / "documents.json", "r", encoding="utf-8") as f:
            documents = json.load(f)
        
        # Create index
        self.create_index(embeddings, chunks, documents)
        
        # Save to disk
        self.save()
        
        logger.info("Index rebuilt from processed data")